"""
Deployment Script for Development Environment

This script automates the deployment of the application to the development environment.
It handles the following tasks:
- Sets environment-specific configurations.
- Deploys the application (simulated).
- Performs a health check to verify the deployment.

Usage:
    python scripts/deploy/dev.py
"""

import os
import random
import sys
import time

# --- Environment-specific Configuration ---
ENV_NAME = "Development"
SERVER_URL = "http://dev.example.com"
DEPLOY_DIR = "/srv/www/dev"


def deploy_application():
    """Deploys the application to the development server (simulated)."""
    print(f"Deploying application to {ENV_NAME} environment...")
    print(f"Target directory: {DEPLOY_DIR}")
    # In a real-world scenario, this would involve copying files,
    # restarting services, etc.
    time.sleep(2)  # Simulate deployment time
    print("Application deployed successfully.")


def health_check():
    """Performs a health check to verify the deployment."""
    print(f"Performing health check on {SERVER_URL}...")
    # Simulate a health check by checking an HTTP endpoint.
    if random.choice([True, True, False]):  # Simulate occasional failure
        print("Health check passed. Application is running correctly.")
    else:
        print("Health check failed. Deployment may have an issue.", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to deploy the application."""
    print(f"--- Starting Deployment to {ENV_NAME} ---")
    deploy_application()
    health_check()
    print(f"--- Deployment to {ENV_NAME} Complete ---")


if __name__ == "__main__":
    main()
