"""
Database Backup Script

This script automates the process of backing up the database.
It handles the following tasks:
- Creates a timestamped backup file.
- Simulates the database dump process.

Usage:
    python scripts/db/backup.py
"""

import os
import time

# --- Configuration ---
BACKUP_DIR = "db/backups"
DB_NAME = "proddb"


def create_backup():
    """Creates a timestamped database backup (simulated)."""
    print("Creating database backup...")
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_file = f"{DB_NAME}-{timestamp}.sql.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_file)

    # In a real scenario, you would use a command like pg_dump or mysqldump.
    print(f"Dumping database to '{backup_path}'...")
    time.sleep(2)  # Simulate backup time
    print("Database backup created successfully.")


def main():
    """Main function to create a database backup."""
    print("--- Starting Database Backup ---")
    create_backup()
    print("--- Database Backup Complete ---")


if __name__ == "__main__":
    main()
