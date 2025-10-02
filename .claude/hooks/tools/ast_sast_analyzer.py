#!/usr/bin/env python3
"""
Comprehensive AST/SAST Analysis Tool

Performs Abstract Syntax Tree and Static Application Security Testing
analysis on the codebase.

Author: System
Version: 1.0.0
"""

import ast
import json
import logging
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Security pattern definitions
SECURITY_PATTERNS = {
    "hardcoded_secrets": [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'key\s*=\s*["\'][A-Za-z0-9+/]{20,}["\']',
    ],
    "sql_injection": [
        r'execute\s*\(\s*["\'][^"\']*%[^"\']*["\']',
        r'query\s*\(\s*["\'][^"\']*\+[^"\']*["\']',
        r"format\s*\([^)]*\%[^)]*\)",
    ],
    "command_injection": [
        r"os\.system\s*\([^)]*\)",
        r"subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True",
        r"eval\s*\([^)]*\)",
        r"exec\s*\([^)]*\)",
    ],
    "path_traversal": [
        r"open\s*\([^)]*\.\.[^)]*\)",
        r'\.\.\/[^"\']*["\']',
        r'\.\.\\[^"\']*["\']',
    ],
    "insecure_ssl": [
        r"ssl_verify\s*=\s*False",
        r"verify\s*=\s*False",
        r"ssl\.create_default_context\s*\([^)]*check_hostname\s*=\s*False",
    ],
}


@dataclass
class CodeMetrics:
    """Code complexity metrics"""

    lines_of_code: int = 0
    function_count: int = 0
    class_count: int = 0
    max_complexity: int = 0
    avg_complexity: float = 0.0
    import_count: int = 0
    docstring_coverage: float = 0.0


@dataclass
class SecurityFinding:
    """Security vulnerability finding"""

    severity: str
    category: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str


@dataclass
class DependencyInfo:
    """Dependency information"""

    name: str
    import_type: str  # 'standard', 'third_party', 'local'
    usage_count: int
    files: List[str]


@dataclass
class FunctionAnalysis:
    """Function analysis results"""

    name: str
    file_path: str
    line_number: int
    complexity: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    calls_made: List[str]
    security_issues: List[SecurityFinding]


class ASTSASTAnalyzer:
    """Comprehensive AST/SAST analyzer"""

    def __init__(self, root_path: str):
        """Initialize analyzer with root path"""
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)

        # Analysis results
        self.files_analyzed: List[str] = []
        self.code_metrics: Dict[str, CodeMetrics] = {}
        self.security_findings: List[SecurityFinding] = []
        self.dependencies: Dict[str, DependencyInfo] = {}
        self.functions: List[FunctionAnalysis] = []
        self.call_graph: Dict[str, List[str]] = defaultdict(list)

        # Compiled patterns for performance
        self.security_regex: Dict[str, List[re.Pattern[str]]] = {}
        for category, patterns in SECURITY_PATTERNS.items():
            self.security_regex[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

        self.logger.info(f"AST/SAST Analyzer initialized for: {self.root_path}")

    def analyze_codebase(self) -> Dict[str, Any]:
        """Perform comprehensive codebase analysis"""
        start_time = datetime.now()

        self.logger.info("Starting comprehensive AST/SAST analysis...")

        # Phase 1: Inventory Discovery
        python_files = self._discover_python_files()
        config_files = self._discover_config_files()

        self.logger.info(
            f"Discovered {len(python_files)} Python files, {len(config_files)} config files"
        )

        # Phase 2: AST Analysis
        for file_path in python_files:
            try:
                self._analyze_python_file(file_path)
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {str(e)}")

        # Phase 3: SAST Security Analysis
        self._perform_security_analysis(python_files)

        # Phase 4: Configuration Analysis
        for file_path in config_files:
            try:
                self._analyze_config_file(file_path)
            except Exception as e:
                self.logger.error(f"Error analyzing config {file_path}: {str(e)}")

        # Phase 5: Generate comprehensive report
        analysis_time = (datetime.now() - start_time).total_seconds()

        report = self._generate_comprehensive_report(analysis_time)

        self.logger.info(f"Analysis completed in {analysis_time:.2f} seconds")
        return report

    def _discover_python_files(self) -> List[Path]:
        """Discover all Python files in the codebase"""
        python_files = []

        patterns = [
            "**/*.py",
            "**/src/**/*.py",
            "**/config/**/*.py",
            "**/tests/**/*.py",
        ]

        for pattern in patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and file_path not in python_files:
                    python_files.append(file_path)

        # Filter out __pycache__ and build directories
        filtered_files = [
            f
            for f in python_files
            if "__pycache__" not in str(f) and "build" not in str(f)
        ]

        return sorted(filtered_files)

    def _discover_config_files(self) -> List[Path]:
        """Discover configuration files"""
        config_files = []

        patterns = ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.ini", "**/*.cfg"]

        for pattern in patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file():
                    config_files.append(file_path)

        return sorted(config_files)

    def _analyze_python_file(self, file_path: Path) -> None:
        """Analyze individual Python file using AST"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            # Initialize file metrics
            file_key = str(file_path.relative_to(self.root_path))
            self.files_analyzed.append(file_key)

            metrics = CodeMetrics()
            metrics.lines_of_code = len(content.splitlines())

            # Visit AST nodes
            visitor = ASTVisitor(
                file_path, metrics, self.dependencies, self.functions, self.call_graph
            )
            visitor.visit(tree)

            # Update metrics
            self.code_metrics[file_key] = metrics

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {str(e)}")

    def _perform_security_analysis(self, files: List[Path]) -> None:
        """Perform SAST security analysis"""
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                self._check_security_patterns(file_path, content)

            except Exception as e:
                self.logger.error(
                    f"Error in security analysis for {file_path}: {str(e)}"
                )

    def _check_security_patterns(self, file_path: Path, content: str) -> None:
        """Check for security vulnerability patterns"""
        lines = content.splitlines()

        for category, patterns in self.security_regex.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        finding = SecurityFinding(
                            severity=self._get_severity(category),
                            category=category,
                            description=f"{category.replace('_', ' ').title()} detected",
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_number=line_num,
                            code_snippet=line.strip(),
                            recommendation=self._get_recommendation(category),
                        )
                        self.security_findings.append(finding)

    def _get_severity(self, category: str) -> str:
        """Get severity level for security category"""
        severity_map = {
            "hardcoded_secrets": "HIGH",
            "sql_injection": "HIGH",
            "command_injection": "CRITICAL",
            "path_traversal": "MEDIUM",
            "insecure_ssl": "MEDIUM",
        }
        return severity_map.get(category, "LOW")

    def _get_recommendation(self, category: str) -> str:
        """Get remediation recommendation for security category"""
        recommendations = {
            "hardcoded_secrets": "Use environment variables or secure key management",
            "sql_injection": "Use parameterized queries or ORM",
            "command_injection": "Avoid shell=True, validate inputs",
            "path_traversal": "Validate and sanitize file paths",
            "insecure_ssl": "Enable SSL verification for security",
        }
        return recommendations.get(category, "Review and remediate security issue")

    def _analyze_config_file(self, file_path: Path) -> None:
        """Analyze configuration files for security issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for credentials in config files
            self._check_config_security(file_path, content)

        except Exception as e:
            self.logger.error(f"Error analyzing config {file_path}: {str(e)}")

    def _check_config_security(self, file_path: Path, content: str) -> None:
        """Check configuration files for security issues"""
        lines = content.splitlines()

        # Patterns specific to config files
        config_patterns = [
            (r'password["\s]*[:=]["\s]*[^"\']+', "Plaintext password in config"),
            (r'secret["\s]*[:=]["\s]*[^"\']+', "Secret key in config"),
            (r'token["\s]*[:=]["\s]*[^"\']+', "Token in config file"),
        ]

        for pattern_str, description in config_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    finding = SecurityFinding(
                        severity="HIGH",
                        category="config_security",
                        description=description,
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_number=line_num,
                        code_snippet=line.strip()[:100],
                        recommendation="Use environment variables or encrypted storage",
                    )
                    self.security_findings.append(finding)

    def _extract_aggregate_metrics(self) -> Dict[str, int]:
        """Extract aggregate code metrics across all files"""
        self.logger.debug(
            "Extracting aggregate metrics from %d analyzed files",
            len(self.code_metrics),
        )

        total_loc = sum(m.lines_of_code for m in self.code_metrics.values())
        total_functions = sum(m.function_count for m in self.code_metrics.values())
        total_classes = sum(m.class_count for m in self.code_metrics.values())

        metrics = {
            "total_loc": total_loc,
            "total_functions": total_functions,
            "total_classes": total_classes,
        }

        self.logger.debug(
            "Aggregate metrics calculated: LOC=%d, Functions=%d, Classes=%d",
            total_loc,
            total_functions,
            total_classes,
        )
        return metrics

    def _extract_security_summary(self) -> Dict[str, Dict[str, int]]:
        """Extract security findings summary by severity and category"""
        self.logger.debug(
            "Extracting security summary from %d findings", len(self.security_findings)
        )

        security_by_severity = Counter(f.severity for f in self.security_findings)
        security_by_category = Counter(f.category for f in self.security_findings)

        summary = {
            "by_severity": dict(security_by_severity),
            "by_category": dict(security_by_category),
        }

        self.logger.debug(
            "Security summary extracted: %d severity types, %d categories",
            len(security_by_severity),
            len(security_by_category),
        )
        return summary

    def _extract_complexity_analysis(self) -> Dict[str, Any]:
        """Extract function complexity analysis and statistics"""
        self.logger.debug(
            "Extracting complexity analysis from %d functions", len(self.functions)
        )

        complexities = [f.complexity for f in self.functions if f.complexity > 0]
        avg_complexity = statistics.mean(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0
        functions_over_10 = len([c for c in complexities if c > 10])

        analysis = {
            "complexities": complexities,
            "avg_complexity": avg_complexity,
            "max_complexity": max_complexity,
            "functions_over_10": functions_over_10,
        }

        self.logger.debug(
            "Complexity analysis: avg=%.2f, max=%d, over_10=%d",
            avg_complexity,
            max_complexity,
            functions_over_10,
        )
        return analysis

    def _extract_dependency_analysis(self) -> Dict[str, Any]:
        """Extract dependency analysis by type and usage"""
        self.logger.debug(
            "Extracting dependency analysis from %d dependencies",
            len(self.dependencies),
        )

        third_party_deps = [
            d for d in self.dependencies.values() if d.import_type == "third_party"
        ]
        local_deps = [d for d in self.dependencies.values() if d.import_type == "local"]

        # Get top dependencies by usage
        top_dependencies = [
            {
                "name": d.name,
                "usage_count": d.usage_count,
                "type": d.import_type,
            }
            for d in sorted(
                self.dependencies.values(),
                key=lambda x: x.usage_count,
                reverse=True,
            )[:20]
        ]

        analysis = {
            "third_party_deps": third_party_deps,
            "local_deps": local_deps,
            "top_dependencies": top_dependencies,
        }

        self.logger.debug(
            "Dependency analysis: %d third-party, %d local, %d top deps",
            len(third_party_deps),
            len(local_deps),
            len(top_dependencies),
        )
        return analysis

    def _extract_architecture_analysis(self) -> Dict[str, Any]:
        """Extract architecture analysis including file complexity rankings"""
        self.logger.debug(
            "Extracting architecture analysis from %d functions", len(self.functions)
        )

        # Calculate file complexity rankings
        file_complexity: Dict[str, List[int]] = {}
        for func in self.functions:
            file_key = func.file_path
            if file_key not in file_complexity:
                file_complexity[file_key] = []
            file_complexity[file_key].append(func.complexity)

        top_complex_files = []
        for file_path, complexities in file_complexity.items():
            avg_file_complexity = statistics.mean(complexities) if complexities else 0
            top_complex_files.append((file_path, avg_file_complexity))

        top_complex_files.sort(key=lambda x: x[1], reverse=True)

        analysis = {
            "file_complexity": file_complexity,
            "top_complex_files": top_complex_files[:10],  # Top 10 most complex files
            "module_structure": self._analyze_module_structure(),
            "call_graph_complexity": len(self.call_graph),
            "circular_dependencies": self._detect_circular_dependencies(),
        }

        self.logger.debug(
            "Architecture analysis: %d files analyzed, top complexity=%.2f",
            len(file_complexity),
            top_complex_files[0][1] if top_complex_files else 0,
        )
        return analysis

    def _generate_comprehensive_report(self, analysis_time: float) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        self.logger.debug("Starting comprehensive report generation")

        # Extract aggregate metrics using helper function
        aggregate_metrics = self._extract_aggregate_metrics()

        # Extract security summary using helper function
        security_summary = self._extract_security_summary()

        # Extract complexity analysis using helper function
        complexity_analysis = self._extract_complexity_analysis()

        # Extract dependency analysis using helper function
        dependency_analysis = self._extract_dependency_analysis()

        # Extract architecture analysis using helper function
        architecture_analysis = self._extract_architecture_analysis()

        self.logger.debug(
            "Assembling comprehensive report with all extracted components"
        )

        report = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_duration_seconds": analysis_time,
                "analyzer_version": "1.0.0",
            },
            "executive_summary": {
                "total_files_analyzed": len(self.files_analyzed),
                "total_lines_of_code": aggregate_metrics["total_loc"],
                "total_functions": aggregate_metrics["total_functions"],
                "total_classes": aggregate_metrics["total_classes"],
                "security_findings_total": len(self.security_findings),
                "critical_findings": security_summary["by_severity"].get("CRITICAL", 0),
                "high_findings": security_summary["by_severity"].get("HIGH", 0),
                "medium_findings": security_summary["by_severity"].get("MEDIUM", 0),
                "code_health_score": self._calculate_health_score(),
            },
            "code_metrics": {
                "complexity_analysis": {
                    "average_function_complexity": round(
                        complexity_analysis["avg_complexity"], 2
                    ),
                    "maximum_function_complexity": complexity_analysis[
                        "max_complexity"
                    ],
                    "functions_over_10_complexity": complexity_analysis[
                        "functions_over_10"
                    ],
                    "total_functions_analyzed": len(self.functions),
                },
                "file_metrics": dict(self.code_metrics),
                "top_complex_files": architecture_analysis["top_complex_files"],
            },
            "security_analysis": {
                "findings_by_severity": security_summary["by_severity"],
                "findings_by_category": security_summary["by_category"],
                "detailed_findings": [
                    asdict(f) for f in self.security_findings[:50]
                ],  # Limit for report size
            },
            "dependency_analysis": {
                "total_dependencies": len(self.dependencies),
                "third_party_count": len(dependency_analysis["third_party_deps"]),
                "local_dependencies_count": len(dependency_analysis["local_deps"]),
                "top_dependencies": dependency_analysis["top_dependencies"],
            },
            "architecture_analysis": {
                "module_structure": architecture_analysis["module_structure"],
                "call_graph_complexity": architecture_analysis["call_graph_complexity"],
                "circular_dependencies": architecture_analysis["circular_dependencies"],
            },
            "recommendations": self._generate_recommendations(),
        }

        self.logger.info("Comprehensive report generated with %d sections", len(report))

        return report

    def _calculate_health_score(self) -> int:
        """Calculate overall code health score (0-100)"""
        score = 100

        # Apply security penalty
        score -= self._calculate_security_penalty()

        # Apply complexity penalty
        score -= self._calculate_complexity_penalty()

        # Apply documentation penalty
        score -= self._calculate_documentation_penalty()

        return max(0, min(100, score))

    def _calculate_security_penalty(self) -> int:
        """Calculate penalty points for security findings.

        Returns:
            Total penalty points for security issues
        """
        critical_penalty = (
            len([f for f in self.security_findings if f.severity == "CRITICAL"]) * 20
        )
        high_penalty = (
            len([f for f in self.security_findings if f.severity == "HIGH"]) * 10
        )
        medium_penalty = (
            len([f for f in self.security_findings if f.severity == "MEDIUM"]) * 5
        )

        return critical_penalty + high_penalty + medium_penalty

    def _calculate_complexity_penalty(self) -> int:
        """Calculate penalty points for high complexity functions.

        Returns:
            Total penalty points for complexity issues
        """
        complexities = [f.complexity for f in self.functions if f.complexity > 0]
        high_complexity_count = len([c for c in complexities if c > 15])
        return high_complexity_count * 2

    def _calculate_documentation_penalty(self) -> int:
        """Calculate penalty points for poor documentation.

        Returns:
            Penalty points for documentation issues
        """
        if not self.functions:
            return 0

        documented_functions = len([f for f in self.functions if f.docstring])
        doc_ratio = documented_functions / len(self.functions)

        return 10 if doc_ratio < 0.5 else 0

    def _analyze_module_structure(self) -> Dict[str, Any]:
        """Analyze module structure and organization"""
        structure: Dict[str, List[str]] = {
            "src_modules": [],
            "test_modules": [],
            "config_modules": [],
            "utility_modules": [],
        }

        for file_path in self.files_analyzed:
            path = Path(file_path)

            if "src" in path.parts:
                structure["src_modules"].append(str(path))
            elif "test" in path.parts:
                structure["test_modules"].append(str(path))
            elif "config" in path.parts:
                structure["config_modules"].append(str(path))
            else:
                structure["utility_modules"].append(str(path))

        return structure

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in import graph"""
        # Simplified circular dependency detection
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.call_graph.get(node, []):
                dfs(neighbor, path + [neighbor])

            rec_stack.remove(node)

        for node in self.call_graph:
            if node not in visited:
                dfs(node, [node])

        return cycles

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Security recommendations
        critical_findings = [
            f for f in self.security_findings if f.severity == "CRITICAL"
        ]
        if critical_findings:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Security",
                    "title": "Address Critical Security Vulnerabilities",
                    "description": f"Found {
                        len(critical_findings)} critical security issues requiring immediate attention",
                    "effort": "High",
                }
            )

        # Complexity recommendations
        high_complexity_functions = [f for f in self.functions if f.complexity > 15]
        if high_complexity_functions:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Code Quality",
                    "title": "Refactor High Complexity Functions",
                    "description": f"Found {len(high_complexity_functions)} functions with complexity > 15",
                    "effort": "Medium",
                }
            )

        # Documentation recommendations
        undocumented_functions = [f for f in self.functions if not f.docstring]
        if len(undocumented_functions) > len(self.functions) * 0.5:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Documentation",
                    "title": "Improve Documentation Coverage",
                    "description": f"{len(undocumented_functions)} functions lack documentation",
                    "effort": "Low",
                }
            )

        return recommendations


class ASTVisitor(ast.NodeVisitor):
    """AST visitor for code analysis"""

    def __init__(
        self,
        file_path: Path,
        metrics: CodeMetrics,
        dependencies: Dict[str, DependencyInfo],
        functions: List[FunctionAnalysis],
        call_graph: Dict[str, List[str]],
    ):
        self.file_path = file_path
        self.metrics = metrics
        self.dependencies = dependencies
        self.functions = functions
        self.call_graph = call_graph
        self.current_function: Optional[FunctionAnalysis] = None
        self.complexity_stack = [0]

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements"""
        for alias in node.names:
            self._record_dependency(alias.name)
        self.metrics.import_count += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from imports"""
        if node.module:
            self._record_dependency(node.module)
        self.metrics.import_count += len(node.names)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions"""
        self.metrics.function_count += 1

        # Calculate complexity
        complexity = self._calculate_complexity(node)

        # Extract function info
        func_analysis = FunctionAnalysis(
            name=node.name,
            file_path=str(self.file_path.relative_to(Path.cwd())),
            line_number=node.lineno,
            complexity=complexity,
            parameters=[arg.arg for arg in node.args.args],
            return_type=None,  # Could extract from annotations
            docstring=ast.get_docstring(node),
            calls_made=[],
            security_issues=[],
        )

        self.functions.append(func_analysis)

        # Track function calls within this function
        old_function = self.current_function
        self.current_function = func_analysis

        self.generic_visit(node)

        self.current_function = old_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions"""
        self.metrics.class_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls"""
        if self.current_function:
            call_name = self._get_call_name(node)
            if call_name:
                self.current_function.calls_made.append(call_name)
                self.call_graph[self.current_function.name].append(call_name)

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statements (increase complexity)"""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops (increase complexity)"""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loops (increase complexity)"""
        self.complexity_stack[-1] += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statements (increase complexity)"""
        self.complexity_stack[-1] += len(node.handlers)
        self.generic_visit(node)

    def _record_dependency(self, module_name: str) -> None:
        """Record module dependency"""
        import_type = self._classify_import(module_name)

        if module_name not in self.dependencies:
            self.dependencies[module_name] = DependencyInfo(
                name=module_name, import_type=import_type, usage_count=0, files=[]
            )

        self.dependencies[module_name].usage_count += 1
        file_path = str(self.file_path.relative_to(Path.cwd()))
        if file_path not in self.dependencies[module_name].files:
            self.dependencies[module_name].files.append(file_path)

    def _classify_import(self, module_name: str) -> str:
        """Classify import as standard, third_party, or local"""
        import sys

        if module_name in sys.stdlib_module_names:
            return "standard"
        elif module_name.startswith(".") or "src" in module_name:
            return "local"
        else:
            return "third_party"

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, (ast.BoolOp, ast.Compare)):
                complexity += 1

        return complexity

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract function call name"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None


def main() -> None:
    """Main execution function"""
    logging.basicConfig(level=logging.INFO)

    # Initialize analyzer
    root_path = Path.cwd()
    analyzer = ASTSASTAnalyzer(str(root_path))

    # Perform analysis
    report = analyzer.analyze_codebase()

    # Generate outputs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON Report
    json_file = root_path / f"ast_sast_report_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    # Summary Report
    summary_file = root_path / f"ast_sast_summary_{timestamp}.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(generate_markdown_summary(report))

    print("Analysis completed!")
    print(f"JSON Report: {json_file}")
    print(f"Summary Report: {summary_file}")
    print("Summary:")
    print(f"   Files Analyzed: {report['executive_summary']['total_files_analyzed']}")
    print(f"   Lines of Code: {report['executive_summary']['total_lines_of_code']:,}")
    print(
        f"   Security Findings: {report['executive_summary']['security_findings_total']}"
    )
    print(
        f"   Code Health Score: {report['executive_summary']['code_health_score']}/100"
    )


def generate_markdown_summary(report: Dict[str, Any]) -> str:
    """Generate markdown summary report"""
    summary = f"""# AST/SAST Analysis Report

## Executive Summary

**Analysis Date**: {report['metadata']['analysis_timestamp']}
**Analysis Duration**: {report['metadata']['analysis_duration_seconds']:.2f} seconds
**Code Health Score**: {report['executive_summary']['code_health_score']}/100

### Key Metrics
- **Files Analyzed**: {report['executive_summary']['total_files_analyzed']}
- **Lines of Code**: {report['executive_summary']['total_lines_of_code']:,}
- **Functions**: {report['executive_summary']['total_functions']}
- **Classes**: {report['executive_summary']['total_classes']}

### Security Findings
- **Critical**: {report['executive_summary']['critical_findings']}
- **High**: {report['executive_summary']['high_findings']}
- **Medium**: {report['executive_summary']['medium_findings']}

## Code Quality Analysis

### Complexity Metrics
- **Average Function Complexity**: {report['code_metrics']['complexity_analysis']['average_function_complexity']}
- **Maximum Function Complexity**: {report['code_metrics']['complexity_analysis']['maximum_function_complexity']}
- **Functions Over 10 Complexity**: {report['code_metrics']['complexity_analysis']['functions_over_10_complexity']}

### Top Complex Files
"""

    for file_path, complexity in report["code_metrics"]["top_complex_files"][:5]:
        summary += f"- `{file_path}`: {complexity:.1f}\n"

    summary += """
## Security Analysis

### Findings by Category
"""

    for category, count in report["security_analysis"]["findings_by_category"].items():
        summary += f"- **{category.replace('_', ' ').title()}**: {count}\n"

    summary += f"""
## Dependencies

- **Total Dependencies**: {report['dependency_analysis']['total_dependencies']}
- **Third-party Libraries**: {report['dependency_analysis']['third_party_count']}
- **Local Modules**: {report['dependency_analysis']['local_dependencies_count']}

### Top Dependencies
"""

    for dep in report["dependency_analysis"]["top_dependencies"][:10]:
        summary += f"- **{dep['name']}** ({dep['type']}): {dep['usage_count']} usages\n"

    summary += "\n## Recommendations\n\n"

    for rec in report["recommendations"]:
        summary += f"### {rec['priority']}: {rec['title']}\n"
        summary += f"**Category**: {rec['category']}\n"
        summary += f"**Description**: {rec['description']}\n"
        summary += f"**Effort**: {rec['effort']}\n\n"

    return summary


if __name__ == "__main__":
    main()
