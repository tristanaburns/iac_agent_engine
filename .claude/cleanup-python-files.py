#!/usr/bin/env python3
"""
Simple Python Cache Cleanup Script
Removes Python cache and linting tool cache directories
Keeps ALL Python source files and other important files
"""

import shutil
from pathlib import Path

# Configuration - Portable: Works from any directory
SCRIPT_DIR = Path(__file__).parent.resolve()
CLAUDE_DIR = SCRIPT_DIR
DRY_RUN = False  # Set to True to see what would be deleted

# Cache directories to remove (these are auto-generated)
CACHE_DIRS = [
    "__pycache__",
    ".ruff_cache",
    ".black_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".pylint.d",
    ".bandit",
    ".safety",
    ".flake8_cache",
    ".tox",
]


def cleanup_cache_dirs():
    """Remove cache directories recursively"""
    removed_count = 0

    print("Cleaning up Python cache directories...")
    print("=" * 40)

    for cache_dir in CACHE_DIRS:
        # Find all instances of this cache directory
        for path in CLAUDE_DIR.rglob(cache_dir):
            if path.is_dir():
                if DRY_RUN:
                    print(f"[DRY RUN] Would remove: {path}")
                else:
                    try:
                        shutil.rmtree(path)
                        print(f"Removed: {path}")
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {path}: {e}")

    # Also clean up .pyc files
    pyc_count = 0
    for pyc_file in CLAUDE_DIR.rglob("*.pyc"):
        if DRY_RUN:
            print(f"[DRY RUN] Would remove: {pyc_file}")
        else:
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception as e:
                print(f"Error removing {pyc_file}: {e}")

    if pyc_count > 0:
        print(f"Removed {pyc_count} .pyc files")
        removed_count += pyc_count

    print("=" * 40)
    if DRY_RUN:
        print(f"DRY RUN: Found {removed_count} items that would be cleaned up")
        print("Set DRY_RUN = False to actually clean up")
    else:
        print(f"Cleaned up {removed_count} cache items")

    return removed_count


def main():
    """Main cleanup function"""
    print("Simple Python Cache Cleanup")
    print(f"Working in: {CLAUDE_DIR}")

    if DRY_RUN:
        print("DRY RUN MODE - Nothing will be deleted")

    print()
    cleanup_cache_dirs()


if __name__ == "__main__":
    main()
