"""Path resolution utilities following SOLID principles.

Single Responsibility: Only handles path resolution logic.
"""

from pathlib import Path
from typing import List, Optional


class PathResolver:
    """Resolves paths relative to hook installation location."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with base path (defaults to hooks directory)."""
        if base_path is None:
            # Get path relative to this module
            self.base_path = Path(__file__).parent.parent.resolve()
        else:
            self.base_path = Path(base_path).resolve()

        # Cache commonly used paths
        self._claude_dir = self.base_path.parent
        self._project_dir = self._claude_dir.parent

    @property
    def hooks_dir(self) -> Path:
        """Get hooks directory path."""
        return self.base_path

    @property
    def claude_dir(self) -> Path:
        """Get .claude directory path."""
        return self._claude_dir

    @property
    def project_dir(self) -> Path:
        """Get project directory path."""
        return self._project_dir

    @property
    def tools_dir(self) -> Path:
        """Get tools directory path."""
        return self.base_path / "tools"

    @property
    def quality_checks_dir(self) -> Path:
        """Get quality checks directory path."""
        return self.claude_dir / "hooks" / "quality-checks"

    @property
    def backups_dir(self) -> Path:
        """Get backups directory path."""
        return self.claude_dir / "backups"

    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        return self.claude_dir / "logs"

    def resolve_file(self, relative_path: str) -> Path:
        """Resolve a file path relative to base directory."""
        return (self.base_path / relative_path).resolve()

    def ensure_directory(self, path: Path) -> Path:
        """Ensure directory exists, creating if necessary."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def find_git_root(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """Find the git repository root from a starting path."""
        if start_path is None:
            start_path = self.project_dir

        current = Path(start_path).resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None

    def get_python_files(self, directory: Optional[Path] = None) -> List[Path]:
        """Get all Python files in a directory."""
        if directory is None:
            directory = self.project_dir

        return list(Path(directory).rglob("*.py"))
