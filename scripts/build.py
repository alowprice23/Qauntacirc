"""
Build System Script

This script automates the build process for the project.
It handles the following tasks:
- Cleans previous build artifacts.
- Reads the version from a file.
- Creates a source distribution and wheel.
- Manages build artifacts.

Usage:
    python scripts/build.py
"""

import os
import shutil
import subprocess
import sys

# --- Configuration ---
BUILD_DIR = "build"
DIST_DIR = "dist"
VERSION_FILE = "VERSION"
ARTIFACTS_TO_KEEP = 5


def clean_build_artifacts():
    """Removes previous build artifacts."""
    print("Cleaning build artifacts...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory: {directory}")


def get_project_version():
    """Reads the project version from the VERSION file."""
    if not os.path.exists(VERSION_FILE):
        print(f"Error: '{VERSION_FILE}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(VERSION_FILE, "r") as f:
        version = f.read().strip()
    print(f"Project version: {version}")
    return version


def create_dummy_setup_py():
    """Creates a dummy setup.py for build purposes if it doesn't exist."""
    if os.path.exists("setup.py"):
        return

    print("Creating dummy 'setup.py' for build...")
    with open("setup.py", "w") as f:
        f.write('from setuptools import setup, find_packages\n')
        f.write('setup(name="myproject", version="0.1.0", packages=find_packages())\n')


def build_distribution():
    """Builds the source distribution and wheel."""
    print("Building distribution...")
    create_dummy_setup_py()
    # In a real project, this would be more complex.
    # We are simulating the build process using setuptools.
    subprocess.check_call([sys.executable, "setup.py", "sdist", "bdist_wheel"])
    print("Distribution built successfully.")


def manage_artifacts():
    """Manages build artifacts, keeping only a limited number."""
    if not os.path.exists(DIST_DIR):
        return

    artifacts = sorted(
        os.listdir(DIST_DIR),
        key=lambda f: os.path.getmtime(os.path.join(DIST_DIR, f)),
    )
    if len(artifacts) > ARTIFACTS_TO_KEEP:
        print("Cleaning up old artifacts...")
        for artifact in artifacts[:-ARTIFACTS_TO_KEEP]:
            os.remove(os.path.join(DIST_DIR, artifact))
            print(f"Removed old artifact: {artifact}")


def main():
    """Main function to run the build process."""
    print("--- Starting Build Process ---")
    clean_build_artifacts()
    version = get_project_version()
    # In a real scenario, you might inject this version into your code.
    build_distribution()
    manage_artifacts()
    print(f"--- Build Process for Version {version} Complete ---")


if __name__ == "__main__":
    if not os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "w") as f:
            f.write("0.1.0")
    main()
