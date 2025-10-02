#!/usr/bin/env python3
"""
Auto Unicode Cleanup Solution.

=============================

Real-time file watcher that monitors for file changes and runs unicode cleanup
immediately. This solution works around the PostToolUse hook limitation in Claude Code.

Features:
- Background file monitoring with instant cleanup
- Standalone script mode for manual cleanup
- Session tracking for all modified files
- Windows console compatibility

Usage:
    python auto_unicode_cleanup.py --watch      # Background file watcher
    python auto_unicode_cleanup.py --cleanup    # Manual cleanup
    python auto_unicode_cleanup.py --session    # Clean all session files

Author: System
Version: 1.0.0
"""

import argparse
import json
import logging
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Add tools directory to Python path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

try:
    from .unicode_manager import UnicodeManager
except ImportError:
    print("[ERROR] Could not import UnicodeManager")
    sys.exit(1)


class UnicodeCleanupHandler(FileSystemEventHandler):
    """File system event handler for unicode cleanup."""

    def __init__(
        self, unicode_manager: UnicodeManager, session_tracker: "SessionTracker"
    ) -> None:
        """Initialize the unicode cleanup handler.

        Args:
            unicode_manager: Unicode manager instance
            session_tracker: Session tracker instance
        """
        self.unicode_manager = unicode_manager
        self.session_tracker = session_tracker
        self.processed_files: Set[str] = set()
        self.cooldown_seconds = 2  # Prevent duplicate processing
        self.last_processed: Dict[str, float] = {}

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Skip backup files
        if file_path.name.endswith(".backup"):
            return False

        # Skip files in excluded directories
        excluded_dirs = {
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
            "backups",
            ".tox",
            "site-packages",
            "logs",
        }

        for part in file_path.parts:
            if part in excluded_dirs:
                return False

        # Only process text files
        text_extensions = {".py", ".md", ".txt", ".yml", ".yaml", ".json", ".js", ".ts"}
        if file_path.suffix not in text_extensions:
            return False

        # Cooldown check
        file_str = str(file_path)
        current_time = time.time()
        if file_str in self.last_processed:
            if current_time - self.last_processed[file_str] < self.cooldown_seconds:
                return False

        return True

    def process_file_safely(self, file_path: Path) -> None:
        """Process file with error handling."""
        try:
            if not self.should_process_file(file_path):
                return

            # Update cooldown
            self.last_processed[str(file_path)] = time.time()

            # Track in session
            self.session_tracker.add_file(file_path)

            # Process unicode cleanup
            result = self.unicode_manager.process_file(file_path)

            if result["modified"]:
                timestamp = datetime.now().strftime("%H:%M:%S")
                replacements = result["unicode_replaced"]
                print(
                    f"[{timestamp}] Unicode cleaned: {file_path.name} "
                    f"({replacements} replacements)"
                )

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")

    def on_modified(self, event):
        """Handle file modification events."""
        if not isinstance(event, FileModifiedEvent) or event.is_directory:
            return

        file_path = Path(event.src_path)
        # Run in background thread to avoid blocking the watcher
        threading.Thread(
            target=self.process_file_safely, args=(file_path,), daemon=True
        ).start()

    def on_created(self, event):
        """Handle file creation events."""
        if not isinstance(event, FileCreatedEvent) or event.is_directory:
            return

        file_path = Path(event.src_path)
        # Small delay to ensure file is fully written
        threading.Thread(
            target=lambda: (time.sleep(0.5), self.process_file_safely(file_path)),
            daemon=True,
        ).start()


class SessionTracker:
    """Tracks modified files during the current session."""

    def __init__(self) -> None:
        """Initialize the session tracker."""
        self.session_file = Path(".claude/hooks/tools/unicode_session.json")
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.modified_files: Set[str] = set()
        self.session_start = datetime.now()
        self.load_session()

    def load_session(self) -> None:
        """Load existing session data."""
        try:
            if self.session_file.exists():
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    # Only load files from last 24 hours
                    session_start = datetime.fromisoformat(
                        data.get("session_start", datetime.now().isoformat())
                    )
                    if datetime.now() - session_start < timedelta(hours=24):
                        self.modified_files = set(data.get("modified_files", []))
                        self.session_start = session_start
        except Exception as e:
            print(f"[WARN] Could not load session data: {e}")

    def save_session(self) -> None:
        """Save current session data."""
        try:
            data = {
                "session_start": self.session_start.isoformat(),
                "modified_files": list(self.modified_files),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.session_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save session data: {e}")

    def add_file(self, file_path: Path) -> None:
        """Add file to session tracking."""
        self.modified_files.add(str(file_path.absolute()))
        self.save_session()

    def get_modified_files(self) -> List[Path]:
        """Get all modified files in current session."""
        valid_files = []
        for file_str in self.modified_files:
            file_path = Path(file_str)
            if file_path.exists():
                valid_files.append(file_path)
        return valid_files


class AutoUnicodeCleanup:
    """Main auto unicode cleanup application."""

    def __init__(self) -> None:
        """Initialize the auto unicode cleanup application."""
        self.unicode_manager = UnicodeManager()
        self.session_tracker = SessionTracker()
        self.observer: Optional[Any] = None

    def start_file_watcher(self, watch_directory: str = ".") -> None:
        """Start background file watcher."""
        abs_path = Path(watch_directory).absolute()
        print(f"[INFO] Starting unicode cleanup file watcher on: {abs_path}")
        print("[INFO] Monitoring for file changes... Press Ctrl+C to stop")

        # Create event handler
        event_handler = UnicodeCleanupHandler(
            self.unicode_manager, self.session_tracker
        )

        # Setup observer
        self.observer = Observer()
        self.observer.schedule(event_handler, watch_directory, recursive=True)

        try:
            self.observer.start()

            # Keep running until interrupted
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n[INFO] File watcher stopped by user")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()

    def cleanup_directory(
        self, directory: str = ".", recursive: bool = True
    ) -> Dict[str, Any]:
        """Run unicode cleanup on directory."""
        print(f"[INFO] Running unicode cleanup on: {Path(directory).absolute()}")

        directory_path = Path(directory)
        result = self.unicode_manager.process_directory(directory_path, recursive)

        # Track all processed files
        if recursive:
            for file_path in directory_path.rglob("*"):
                if file_path.is_file():
                    self.session_tracker.add_file(file_path)
        else:
            for file_path in directory_path.glob("*"):
                if file_path.is_file():
                    self.session_tracker.add_file(file_path)

        return result

    def cleanup_session_files(self) -> Dict[str, Any]:
        """Clean all files modified in current session."""
        modified_files = self.session_tracker.get_modified_files()

        if not modified_files:
            print("[INFO] No modified files found in current session")
            return {"files_processed": 0, "files_modified": 0}

        print(f"[INFO] Cleaning {len(modified_files)} files from current session")

        stats = {"files_processed": 0, "files_modified": 0, "unicode_replaced": 0}

        for file_path in modified_files:
            try:
                result = self.unicode_manager.process_file(file_path)
                if result["processed"]:
                    stats["files_processed"] += 1
                    if result["modified"]:
                        stats["files_modified"] += 1
                        stats["unicode_replaced"] += result["unicode_replaced"]
                        replacements = result["unicode_replaced"]
                        print(
                            f"[INFO] Cleaned: {file_path.name} "
                            f"({replacements} replacements)"
                        )
            except Exception as e:
                print(f"[ERROR] Failed to process {file_path}: {e}")

        return stats

    def cleanup_recent_files(self, hours: int = 2) -> Dict[str, Any]:
        """Clean files modified in the last N hours."""
        print(f"[INFO] Cleaning files modified in last {hours} hours")

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_files = []

        # Scan current directory for recent files
        for file_path in Path(".").rglob("*"):
            if file_path.is_file():
                try:
                    # Check modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime > cutoff_time:
                        recent_files.append(file_path)
                except Exception:
                    continue

        if not recent_files:
            print("[INFO] No recently modified files found")
            return {"files_processed": 0, "files_modified": 0}

        print(f"[INFO] Found {len(recent_files)} recently modified files")

        stats = {"files_processed": 0, "files_modified": 0, "unicode_replaced": 0}

        for file_path in recent_files:
            try:
                # Track in session
                self.session_tracker.add_file(file_path)

                result = self.unicode_manager.process_file(file_path)
                if result["processed"]:
                    stats["files_processed"] += 1
                    if result["modified"]:
                        stats["files_modified"] += 1
                        stats["unicode_replaced"] += result["unicode_replaced"]
                        replacements = result["unicode_replaced"]
                        print(
                            f"[INFO] Cleaned: {file_path.name} "
                            f"({replacements} replacements)"
                        )
            except Exception as e:
                print(f"[ERROR] Failed to process {file_path}: {e}")

        return stats


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Auto Unicode Cleanup Solution")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--watch", action="store_true", help="Start background file watcher"
    )
    group.add_argument(
        "--cleanup", action="store_true", help="Run manual cleanup on current directory"
    )
    group.add_argument(
        "--session",
        action="store_true",
        help="Clean all files modified in current session",
    )
    group.add_argument(
        "--recent",
        type=int,
        metavar="HOURS",
        help="Clean files modified in last N hours",
    )

    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to watch/cleanup (default: current)",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        default=True,
        help="Recursive processing",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Create cleanup instance
    cleanup = AutoUnicodeCleanup()

    try:
        if args.watch:
            cleanup.start_file_watcher(args.directory)

        elif args.cleanup:
            result = cleanup.cleanup_directory(args.directory, args.recursive)
            files_processed = result["files_processed"]
            files_modified = result["files_modified"]
            print(
                f"[RESULT] Processed {files_processed} files, "
                f"modified {files_modified}"
            )

        elif args.session:
            result = cleanup.cleanup_session_files()
            files_processed = result["files_processed"]
            files_modified = result["files_modified"]
            print(
                f"[RESULT] Processed {files_processed} files, "
                f"modified {files_modified}"
            )

        elif args.recent:
            result = cleanup.cleanup_recent_files(args.recent)
            files_processed = result["files_processed"]
            files_modified = result["files_modified"]
            print(
                f"[RESULT] Processed {files_processed} files, "
                f"modified {files_modified}"
            )

    except Exception as e:
        print(f"[ERROR] Operation failed: {e}")
        sys.exit(1)

    print("[INFO] Unicode cleanup operation completed")


if __name__ == "__main__":
    main()
