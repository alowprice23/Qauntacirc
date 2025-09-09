"""
Cleanup Script

This script cleans up temporary files, build artifacts, and caches.
It helps to keep the project directory clean.

Usage:
    python scripts/utils/cleanup.py
"""

import os
import shutil

# --- Configuration ---
DIRECTORIES_TO_CLEAN = ["build", "dist", ".pytest_cache", "htmlcov"]
FILE_PATTERNS_TO_CLEAN = [".pyc", ".pyo", ".log"]


def clean_directories():
    """Removes specified directories."""
    print("Cleaning directories...")
    for directory in DIRECTORIES_TO_CLEAN:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory: {directory}")


def clean_files():
    """Removes files matching specified patterns."""
    print("Cleaning files...")
    for root, _, files in os.walk("."):
        for file in files:
            if any(file.endswith(pattern) for pattern in FILE_PATTERNS_TO_CLEAN):
                filepath = os.path.join(root, file)
                os.remove(filepath)
                print(f"Removed file: {filepath}")


def main():
    """Main function to run the cleanup process."""
    print("--- Starting Cleanup ---")
    clean_directories()
    clean_files()
    print("--- Cleanup Complete ---")


if __name__ == "__main__":
    main()
