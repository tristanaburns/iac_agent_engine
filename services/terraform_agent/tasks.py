"""
Celery tasks for Terraform operations
Async execution of Terraform commands with comprehensive error handling
"""

from datetime import datetime
import json
import os
from pathlib import Path
import subprocess  # nosec B404
from typing import Any, Dict, List, Optional

from celery import Celery, Task
from models import JobStatus
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Celery app (will be initialized by main app)
celery_app = Celery("terraform_agent")


class TerraformTask(Task):  # type: ignore[misc]
    """Base class for Terraform tasks with common functionality"""

    def __init__(self) -> None:
        self.workspace_dir = Path("/workspace")
        self.terraform_modules_dir = Path("/terraform/modules")

    def update_job_status(self, job_id: str, status: JobStatus, **kwargs: Any) -> None:
        """Update job status in the global jobs dict"""
        # In a real implementation, this would update the database/redis
        # For now, we'll just log the update
        logger.info("Job status update", job_id=job_id, status=status.value, **kwargs)

    def setup_workspace_directory(self, workspace_name: str) -> Path:
        """Setup workspace directory for Terraform operations"""
        workspace_path = self.workspace_dir / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        return workspace_path

    def run_terraform_command(
        self,
        command: List[str],
        workspace_path: Path,
        timeout: int = 300,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute a Terraform command with proper error handling"""

        # Prepare environment
        terraform_env = os.environ.copy()
        if env:
            terraform_env.update(env)

        # Ensure Terraform data directory is in workspace
        terraform_env["TF_DATA_DIR"] = str(workspace_path / ".terraform")

        full_command = ["terraform"] + command

        logger.info(
            "Executing Terraform command",
            command=" ".join(full_command),
            workspace=str(workspace_path),
        )

        try:
            # Security: Using shell=False and explicit command list for safety
            result = subprocess.run(  # nosec B603
                full_command,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=terraform_env,
                shell=False,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(full_command),
            }

        except subprocess.TimeoutExpired:
            logger.error(
                "Terraform command timed out",
                command=" ".join(full_command),
                timeout=timeout,
            )
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "command": " ".join(full_command),
                "error": "timeout",
            }
        except Exception as e:
            logger.error(
                "Terraform command failed", command=" ".join(full_command), error=str(e)
            )
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(full_command),
                "error": "execution_failed",
            }

    def prepare_variables(
        self, variables: List[Dict[str, Any]], workspace_path: Path
    ) -> List[str]:
        """Prepare Terraform variables for command execution"""
        var_args = []
        var_file_path = workspace_path / "terraform.tfvars.json"

        if variables:
            # Create variables file
            var_data = {}
            for var in variables:
                var_data[var["name"]] = var["value"]

            with open(var_file_path, "w") as f:
                json.dump(var_data, f, indent=2)

            var_args.extend(["-var-file", str(var_file_path)])

        return var_args

    def initialize_terraform(
        self, workspace_path: Path, timeout: int = 300
    ) -> Dict[str, Any]:
        """Initialize Terraform in the workspace"""

        # Copy terraform modules if available
        if self.terraform_modules_dir.exists():
            import shutil

            modules_dest = workspace_path / "modules"
            if modules_dest.exists():
                shutil.rmtree(modules_dest)
            shutil.copytree(self.terraform_modules_dir, modules_dest)
            logger.info(
                "Terraform modules copied",
                source=str(self.terraform_modules_dir),
                dest=str(modules_dest),
            )

        # Run terraform init
        init_result = self.run_terraform_command(
            ["init", "-no-color", "-input=false"], workspace_path, timeout=timeout
        )

        if not init_result["success"]:
            logger.error("Terraform init failed", result=init_result)

        return init_result

    def ensure_terraform_initialized(
        self, workspace_path: Path, job_id: str, timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Ensure Terraform is initialized, return error dict if failed"""
        terraform_dir = workspace_path / ".terraform"
        if not terraform_dir.exists():
            init_result = self.initialize_terraform(workspace_path, timeout)
            if not init_result["success"]:
                self.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Terraform init failed: {init_result['stderr']}",
                    completed_at=datetime.utcnow(),
                )
                return {
                    "success": False,
                    "error": "init_failed",
                    "details": init_result,
                }
        return None

    def prepare_apply_command(
        self,
        auto_approve: bool,
        plan_id: Optional[str],
        workspace_path: Path,
        variables: List[Dict[str, Any]],
        target_resources: List[str],
    ) -> List[str]:
        """Prepare terraform apply command with appropriate arguments"""
        apply_command = ["apply", "-no-color", "-input=false"]

        if auto_approve:
            apply_command.append("-auto-approve")

        # Check for existing plan file
        if plan_id:
            plan_file = workspace_path / f"plan-{plan_id}.tfplan"
            if plan_file.exists():
                apply_command.append(str(plan_file))
                return apply_command
            else:
                logger.warning(
                    "Plan file not found, proceeding with direct apply",
                    plan_file=str(plan_file),
                )

        # Direct apply - add variables and targets
        var_args = self.prepare_variables(variables, workspace_path)
        apply_command.extend(var_args)

        for target in target_resources:
            apply_command.extend(["-target", target])

        return apply_command


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_plan(
    self: TerraformTask,
    job_id: str,
    workspace_name: str,
    destroy: bool = False,
    target_resources: Optional[List[str]] = None,
    variables: Optional[List[Dict[str, Any]]] = None,
    refresh: bool = True,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Execute terraform plan operation"""

    target_resources = target_resources or []
    variables = variables or []

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Initialize Terraform
        init_result = self.initialize_terraform(workspace_path, timeout)
        if not init_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform init failed: {init_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            return {"success": False, "error": "init_failed", "details": init_result}

        # Prepare plan command
        plan_command = ["plan", "-no-color", "-input=false"]

        if destroy:
            plan_command.append("-destroy")

        if not refresh:
            plan_command.append("-refresh=false")

        # Add target resources
        for target in target_resources:
            plan_command.extend(["-target", target])

        # Prepare variables
        var_args = self.prepare_variables(variables, workspace_path)
        plan_command.extend(var_args)

        # Add plan output file
        plan_file = workspace_path / f"plan-{job_id}.tfplan"
        plan_command.extend(["-out", str(plan_file)])

        # Execute plan
        plan_result = self.run_terraform_command(plan_command, workspace_path, timeout)

        result = {
            "success": plan_result["success"],
            "plan_file": str(plan_file) if plan_result["success"] else None,
            "stdout": plan_result["stdout"],
            "stderr": plan_result["stderr"],
            "init_result": init_result,
        }

        if plan_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform plan completed successfully",
                job_id=job_id,
                workspace=workspace_name,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform plan failed: {plan_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform plan failed",
                job_id=job_id,
                workspace=workspace_name,
                error=plan_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform plan task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_apply(
    self: TerraformTask,
    job_id: str,
    workspace_name: str,
    plan_id: Optional[str] = None,
    auto_approve: bool = False,
    target_resources: Optional[List[str]] = None,
    variables: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 600,
) -> Dict[str, Any]:
    """Execute terraform apply operation"""

    target_resources = target_resources or []
    variables = variables or []

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Ensure Terraform is initialized
        init_error = self.ensure_terraform_initialized(workspace_path, job_id, timeout)
        if init_error:
            return init_error

        # Prepare apply command
        apply_command = self.prepare_apply_command(
            auto_approve, plan_id, workspace_path, variables, target_resources
        )

        # Execute apply
        apply_result = self.run_terraform_command(
            apply_command, workspace_path, timeout
        )

        result = {
            "success": apply_result["success"],
            "stdout": apply_result["stdout"],
            "stderr": apply_result["stderr"],
        }

        if apply_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform apply completed successfully",
                job_id=job_id,
                workspace=workspace_name,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform apply failed: {apply_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform apply failed",
                job_id=job_id,
                workspace=workspace_name,
                error=apply_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform apply task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_destroy(
    self: TerraformTask,
    job_id: str,
    workspace_name: str,
    auto_approve: bool = False,
    target_resources: Optional[List[str]] = None,
    variables: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 600,
) -> Dict[str, Any]:
    """Execute terraform destroy operation"""

    target_resources = target_resources or []
    variables = variables or []

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Initialize Terraform if needed
        terraform_dir = workspace_path / ".terraform"
        if not terraform_dir.exists():
            init_result = self.initialize_terraform(workspace_path, timeout)
            if not init_result["success"]:
                self.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Terraform init failed: {init_result['stderr']}",
                    completed_at=datetime.utcnow(),
                )
                return {
                    "success": False,
                    "error": "init_failed",
                    "details": init_result,
                }

        # Prepare destroy command
        destroy_command = ["destroy", "-no-color", "-input=false"]

        if auto_approve:
            destroy_command.append("-auto-approve")

        # Add variables
        var_args = self.prepare_variables(variables, workspace_path)
        destroy_command.extend(var_args)

        # Add target resources
        for target in target_resources:
            destroy_command.extend(["-target", target])

        # Execute destroy
        destroy_result = self.run_terraform_command(
            destroy_command, workspace_path, timeout
        )

        result = {
            "success": destroy_result["success"],
            "stdout": destroy_result["stdout"],
            "stderr": destroy_result["stderr"],
        }

        if destroy_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform destroy completed successfully",
                job_id=job_id,
                workspace=workspace_name,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform destroy failed: {destroy_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform destroy failed",
                job_id=job_id,
                workspace=workspace_name,
                error=destroy_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform destroy task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_import(
    self: TerraformTask,
    job_id: str,
    workspace_name: str,
    address: str,
    resource_id: str,
    variables: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Execute terraform import operation"""

    variables = variables or []

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Initialize Terraform if needed
        terraform_dir = workspace_path / ".terraform"
        if not terraform_dir.exists():
            init_result = self.initialize_terraform(workspace_path, timeout)
            if not init_result["success"]:
                self.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Terraform init failed: {init_result['stderr']}",
                    completed_at=datetime.utcnow(),
                )
                return {
                    "success": False,
                    "error": "init_failed",
                    "details": init_result,
                }

        # Prepare import command
        import_command = ["import", "-no-color", "-input=false"]

        # Add variables
        var_args = self.prepare_variables(variables, workspace_path)
        import_command.extend(var_args)

        # Add address and ID
        import_command.extend([address, resource_id])

        # Execute import
        import_result = self.run_terraform_command(
            import_command, workspace_path, timeout
        )

        result = {
            "success": import_result["success"],
            "stdout": import_result["stdout"],
            "stderr": import_result["stderr"],
            "imported_address": address,
            "imported_id": resource_id,
        }

        if import_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform import completed successfully",
                job_id=job_id,
                workspace=workspace_name,
                address=address,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform import failed: {import_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform import failed",
                job_id=job_id,
                workspace=workspace_name,
                error=import_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform import task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_refresh(
    self: TerraformTask,
    job_id: str,
    workspace_name: str,
    variables: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Execute terraform refresh operation"""

    variables = variables or []

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Initialize Terraform if needed
        terraform_dir = workspace_path / ".terraform"
        if not terraform_dir.exists():
            init_result = self.initialize_terraform(workspace_path, timeout)
            if not init_result["success"]:
                self.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Terraform init failed: {init_result['stderr']}",
                    completed_at=datetime.utcnow(),
                )
                return {
                    "success": False,
                    "error": "init_failed",
                    "details": init_result,
                }

        # Prepare refresh command
        refresh_command = ["refresh", "-no-color", "-input=false"]

        # Add variables
        var_args = self.prepare_variables(variables, workspace_path)
        refresh_command.extend(var_args)

        # Execute refresh
        refresh_result = self.run_terraform_command(
            refresh_command, workspace_path, timeout
        )

        result = {
            "success": refresh_result["success"],
            "stdout": refresh_result["stdout"],
            "stderr": refresh_result["stderr"],
        }

        if refresh_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform refresh completed successfully",
                job_id=job_id,
                workspace=workspace_name,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform refresh failed: {refresh_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform refresh failed",
                job_id=job_id,
                workspace=workspace_name,
                error=refresh_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform refresh task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}


@celery_app.task(bind=True, base=TerraformTask)  # type: ignore[misc]
def execute_terraform_validate(
    self: TerraformTask, job_id: str, workspace_name: str, timeout: int = 120
) -> Dict[str, Any]:
    """Execute terraform validate operation"""

    self.update_job_status(job_id, JobStatus.RUNNING, started_at=datetime.utcnow())

    try:
        # Setup workspace
        workspace_path = self.setup_workspace_directory(workspace_name)

        # Initialize Terraform if needed
        terraform_dir = workspace_path / ".terraform"
        if not terraform_dir.exists():
            init_result = self.initialize_terraform(workspace_path, timeout)
            if not init_result["success"]:
                self.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error_message=f"Terraform init failed: {init_result['stderr']}",
                    completed_at=datetime.utcnow(),
                )
                return {
                    "success": False,
                    "error": "init_failed",
                    "details": init_result,
                }

        # Prepare validate command
        validate_command = ["validate", "-no-color", "-json"]

        # Execute validate
        validate_result = self.run_terraform_command(
            validate_command, workspace_path, timeout
        )

        # Parse validation results
        validation_details = {}
        if validate_result["success"] and validate_result["stdout"]:
            try:
                validation_details = json.loads(validate_result["stdout"])
            except json.JSONDecodeError:
                logger.warning("Failed to parse validation JSON output")

        result = {
            "success": validate_result["success"],
            "stdout": validate_result["stdout"],
            "stderr": validate_result["stderr"],
            "validation_details": validation_details,
        }

        if validate_result["success"]:
            self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                result=result,
            )
            logger.info(
                "Terraform validate completed successfully",
                job_id=job_id,
                workspace=workspace_name,
            )
        else:
            self.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=f"Terraform validate failed: {validate_result['stderr']}",
                completed_at=datetime.utcnow(),
            )
            logger.error(
                "Terraform validate failed",
                job_id=job_id,
                workspace=workspace_name,
                error=validate_result["stderr"],
            )

        return result

    except Exception as e:
        self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error_message=f"Unexpected error: {str(e)}",
            completed_at=datetime.utcnow(),
        )
        logger.error("Terraform validate task failed", job_id=job_id, error=str(e))
        return {"success": False, "error": "task_failed", "details": str(e)}
