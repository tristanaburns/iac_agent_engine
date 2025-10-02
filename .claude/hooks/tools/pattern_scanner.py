#!/usr/bin/env python3
"""
Pattern Scanner.

Scans the entire codebase for forbidden pattern violations and generates
a detailed JSON report according to forbidden_patterns_config.json.

This tool provides comprehensive pattern detection across all Python files
in the codebase and generates detailed violation reports.

Author: System
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PatternScanner:
    """Scans codebase for forbidden pattern violations."""

    def __init__(self, config_path: str, project_root: str):
        """
        Initialize pattern scanner.

        Args:
            config_path: Path to forbidden patterns configuration JSON
            project_root: Root directory of the project to scan
        """
        self.config_path = config_path
        self.project_root = Path(project_root)
        self.patterns: List[Dict[str, Any]] = []
        self.violations: List[Dict[str, Any]] = []
        self.excluded_dirs: Set[str] = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            "dist",
            "build",
            ".mypy_cache",
        }

    def load_patterns(self) -> bool:
        """Load forbidden patterns from configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.patterns = json.load(f)
            logger.info(f"Loaded {len(self.patterns)} forbidden patterns")
            return True
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return False

    def get_python_files(self) -> List[Path]:
        """Get all Python files in the project, excluding certain directories."""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories from the walk
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        logger.info(f"Found {len(python_files)} Python files to scan")
        return python_files

    def scan_file_for_pattern(
        self, file_path: Path, pattern_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Scan a single file for a specific pattern.

        Args:
            file_path: Path to the file to scan
            pattern_config: Pattern configuration from JSON

        Returns:
            List of violations found
        """
        violations: List[Dict[str, Any]] = []
        pattern = pattern_config["pattern"]
        scopes = pattern_config["scope"]

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return violations

        # Compile regex pattern
        try:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
            return violations

        # Check filename violations
        if "file" in scopes:
            filename = file_path.name
            if regex.search(filename):
                violations.append(
                    {
                        "file": str(file_path.relative_to(self.project_root)),
                        "line_number": 0,
                        "line_content": f"Filename: {filename}",
                        "pattern": pattern,
                        "scope": "file",
                        "description": pattern_config["description"],
                        "action_if_found": pattern_config["action_if_found"],
                        "requirement_level": pattern_config["requirement_level"],
                        "violation_type": "filename",
                    }
                )

        # Check content violations
        content_scopes = [s for s in scopes if s != "file"]
        if content_scopes:
            for line_num, line in enumerate(lines, 1):
                matches = regex.finditer(line)
                for match in matches:
                    # Determine violation context
                    violation_type = self._determine_violation_type(
                        line, match, content_scopes
                    )

                    violations.append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "pattern": pattern,
                            "scope": violation_type,
                            "description": pattern_config["description"],
                            "action_if_found": pattern_config["action_if_found"],
                            "requirement_level": pattern_config["requirement_level"],
                            "violation_type": "content",
                            "match_text": match.group(),
                            "match_start": match.start(),
                            "match_end": match.end(),
                        }
                    )

        return violations

    def _determine_violation_type(
        self, line: str, match: re.Match[str], scopes: List[str]
    ) -> str:
        """Determine the specific type of violation based on context."""
        line_stripped = line.strip()

        # Check for specific code contexts
        for scope in scopes:
            if self._matches_scope_context(scope, line_stripped):
                return scope

        # Default fallback
        return self._get_default_scope(scopes)

    def _matches_scope_context(self, scope: str, line_stripped: str) -> bool:
        """Check if line matches the given scope context.

        Args:
            scope: Scope type to check
            line_stripped: Stripped line content

        Returns:
            True if line matches scope context, False otherwise
        """
        scope_patterns = {
            "import_statement": lambda line: "import" in line,
            "code_comment": lambda line: line.startswith("#"),
            "function": lambda line: "def " in line,
            "class": lambda line: "class " in line,
            "try_except": lambda line: "except" in line,
        }

        # Check specific pattern matching
        if scope in scope_patterns:
            return scope_patterns[scope](line_stripped)

        # General scopes that always match
        return scope in ["code_block", "variable", "module"]

    def _get_default_scope(self, scopes: List[str]) -> str:
        """Get default scope when no specific match is found.

        Args:
            scopes: List of available scopes

        Returns:
            Default scope string
        """
        return scopes[0] if scopes else "any"

    def scan_all_files(self) -> None:
        """Scan all Python files for all forbidden patterns."""
        if not self.load_patterns():
            return

        python_files = self.get_python_files()
        self.violations = []

        logger.info("Starting comprehensive pattern scan...")

        for file_path in python_files:
            logger.debug(f"Scanning file: {file_path}")

            for pattern_config in self.patterns:
                file_violations = self.scan_file_for_pattern(file_path, pattern_config)
                self.violations.extend(file_violations)

        logger.info(f"Scan completed. Found {len(self.violations)} total violations")

    def generate_report(self, output_path: str) -> Dict[str, Any]:
        """
        Generate comprehensive violation report.

        Args:
            output_path: Path to save the JSON report

        Returns:
            Report dictionary
        """
        # Organize violations by pattern and file
        violations_by_pattern, violations_by_file = self._organize_violations()

        # Calculate report statistics
        stats = self._calculate_report_statistics(violations_by_file)

        # Generate pattern summary
        pattern_summary = self._create_pattern_summary(violations_by_pattern)

        # Build complete report
        report = self._build_report_dictionary(
            stats, pattern_summary, violations_by_pattern, violations_by_file
        )

        # Save report to file
        self._save_report_to_file(report, output_path)

        return report

    def _organize_violations(
        self,
    ) -> tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        """Organize violations by pattern and file.

        Returns:
            Tuple of (violations_by_pattern, violations_by_file)
        """
        violations_by_pattern: Dict[str, List[Dict[str, Any]]] = {}
        violations_by_file: Dict[str, List[Dict[str, Any]]] = {}

        for violation in self.violations:
            pattern = violation["pattern"]
            file_path = violation["file"]

            if pattern not in violations_by_pattern:
                violations_by_pattern[pattern] = []
            violations_by_pattern[pattern].append(violation)

            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)

        return violations_by_pattern, violations_by_file

    def _calculate_report_statistics(
        self, violations_by_file: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate statistical information for the report.

        Args:
            violations_by_file: Dictionary of violations organized by file

        Returns:
            Dictionary containing calculated statistics
        """
        total_violations = len(self.violations)
        total_files = len(violations_by_file)
        critical_violations = len(
            {v for v in self.violations if v["requirement_level"] == "MUST NOT"}
        )
        compliance_level = self._determine_compliance_level(critical_violations)

        return {
            "total_violations": total_violations,
            "total_files": total_files,
            "critical_violations": critical_violations,
            "compliance_level": compliance_level,
        }

    def _determine_compliance_level(self, critical_violations: int) -> str:
        """Determine compliance level based on critical violations count.

        Args:
            critical_violations: Number of critical violations

        Returns:
            Compliance level string
        """
        if critical_violations > 1000:
            return "CRITICAL"
        elif critical_violations > 100:
            return "HIGH"
        elif critical_violations > 10:
            return "MEDIUM"
        elif critical_violations > 0:
            return "LOW"
        else:
            return "COMPLIANT"

    def _create_pattern_summary(
        self, violations_by_pattern: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Create summary statistics for each pattern.

        Args:
            violations_by_pattern: Dictionary of violations organized by pattern

        Returns:
            List of pattern summary dictionaries
        """
        pattern_summary = []
        for pattern, pattern_violations in violations_by_pattern.items():
            pattern_summary.append(
                {
                    "pattern": pattern,
                    "violation_count": len(pattern_violations),
                    "files_affected": len(set(v["file"] for v in pattern_violations)),
                    "description": (
                        pattern_violations[0]["description"]
                        if pattern_violations
                        else ""
                    ),
                    "requirement_level": (
                        pattern_violations[0]["requirement_level"]
                        if pattern_violations
                        else ""
                    ),
                }
            )

        # Sort by violation count
        pattern_summary.sort(key=lambda x: x["violation_count"], reverse=True)
        return pattern_summary

    def _build_report_dictionary(
        self,
        stats: Dict[str, Any],
        pattern_summary: List[Dict[str, Any]],
        violations_by_pattern: Dict[str, List[Dict[str, Any]]],
        violations_by_file: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Build the complete report dictionary.

        Args:
            stats: Statistical information
            pattern_summary: Pattern summary data
            violations_by_pattern: Violations organized by pattern
            violations_by_file: Violations organized by file

        Returns:
            Complete report dictionary
        """
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_violations": stats["total_violations"],
            "critical_violations": stats["critical_violations"],
            "files_affected": stats["total_files"],
            "compliance_level": stats["compliance_level"],
            "pattern_summary": pattern_summary,
            "violations_by_pattern": violations_by_pattern,
            "violations_by_file": violations_by_file,
            "all_violations": self.violations,
        }

    def _save_report_to_file(self, report: Dict[str, Any], output_path: str) -> None:
        """Save report to JSON file.

        Args:
            report: Report dictionary to save
            output_path: Path to save the report
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print a summary of violations to console."""
        print(f"\n{'=' * 60}")
        print("FORBIDDEN PATTERNS VIOLATION REPORT")
        print(f"{'=' * 60}")
        print(f"Scan Date: {report['scan_timestamp']}")
        print(f"Project Root: {report['project_root']}")
        print(f"Total Violations: {report['total_violations']:,}")
        print(f"Critical Violations: {report['critical_violations']:,}")
        print(f"Files Affected: {report['files_affected']:,}")
        print(f"Compliance Level: {report['compliance_level']}")

        if report["pattern_summary"]:
            print(f"\n{'=' * 60}")
            print("TOP VIOLATION PATTERNS")
            print(f"{'=' * 60}")

            for i, pattern_info in enumerate(report["pattern_summary"][:10], 1):
                print(
                    f"{i:2d}. {pattern_info['pattern'][:40]:<40} "
                    f"{pattern_info['violation_count']:>6,} violations "
                    f"({pattern_info['files_affected']:>3} files)"
                )

        print(f"\n{'=' * 60}")


def main() -> None:
    """Execute main entry point for pattern scanner."""
    parser = argparse.ArgumentParser(
        description="Scan codebase for forbidden pattern violations"
    )
    parser.add_argument(
        "--config",
        default="utils/forbidden_pattern_manager/forbidden_patterns_config.json",
        help="Path to forbidden patterns configuration file",
    )
    parser.add_argument(
        "--project-root", default=".", help="Root directory of project to scan"
    )
    parser.add_argument(
        "--output",
        default="docs/forbidden_patterns_violations.json",
        help="Output path for violations report",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress console output except errors",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    # Initialize scanner
    scanner = PatternScanner(args.config, args.project_root)

    # Run scan
    scanner.scan_all_files()

    # Generate and save report
    report = scanner.generate_report(args.output)

    # Print summary unless quiet mode
    if not args.quiet:
        scanner.print_summary(report)

    # Exit with appropriate code
    if report["critical_violations"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
