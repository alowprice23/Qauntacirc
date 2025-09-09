"""
Development Environment Setup Script

This script automates the setup of the development environment.
It handles the following tasks:
- Creates a virtual environment.
- Installs dependencies from requirements.txt.
- Creates an initial configuration file from a template.

Usage:
    python scripts/setup.py
"""

import os
import subprocess
import sys
import venv

# --- Configuration ---
VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"
CONFIG_TEMPLATE_FILE = "config.template.ini"
CONFIG_FILE = "config.ini"


def create_virtual_environment():
    """Creates a virtual environment if it doesn't already exist."""
    if not os.path.exists(VENV_DIR):
        print(f"Creating virtual environment in '{VENV_DIR}'...")
        venv.create(VENV_DIR, with_pip=True)
        print("Virtual environment created successfully.")
    else:
        print("Virtual environment already exists.")


def install_dependencies():
    """Installs dependencies from the requirements file."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"Error: '{REQUIREMENTS_FILE}' not found.", file=sys.stderr)
        sys.exit(1)

    print("Installing dependencies...")
    pip_executable = os.path.join(VENV_DIR, "bin", "pip")
    subprocess.check_call([pip_executable, "install", "-r", REQUIREMENTS_FILE])
    print("Dependencies installed successfully.")


def create_initial_config():
    """Creates an initial configuration file from a template."""
    if os.path.exists(CONFIG_FILE):
        print(f"'{CONFIG_FILE}' already exists. Skipping creation.")
        return

    if not os.path.exists(CONFIG_TEMPLATE_FILE):
        print(f"Creating dummy '{CONFIG_TEMPLATE_FILE}'...")
        with open(CONFIG_TEMPLATE_FILE, "w") as f:
            f.write("[database]\n")
            f.write("host = localhost\n")
            f.write("port = 5432\n")

    print(f"Creating '{CONFIG_FILE}' from '{CONFIG_TEMPLATE_FILE}'...")
    with open(CONFIG_TEMPLATE_FILE, "r") as f_template:
        with open(CONFIG_FILE, "w") as f_config:
            f_config.write(f_template.read())
    print("Configuration file created successfully.")


def main():
    """Main function to set up the environment."""
    print("--- Starting Development Environment Setup ---")
    create_virtual_environment()
    install_dependencies()
    create_initial_config()
    print("--- Environment Setup Complete ---")


if __name__ == "__main__":
    main()
