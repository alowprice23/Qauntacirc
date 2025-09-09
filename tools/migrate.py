# tools/migrate.py
"""
Data and schema migration tools for QuantaCirc.

This module provides a simple framework for managing data migrations as the
system's schemas and data formats evolve. It helps in automating version
upgrades and ensuring data consistency.

Key Features:
- A version-based migration system.
- Functions for data transformation between schema versions.
- Automation for applying migrations.
"""

from typing import Dict, Any, Callable

import os
import importlib.util
import re
from typing import Dict, Any, Callable, List, Tuple

MIGRATION_DIR = "migrations"
MIGRATION_TEMPLATE = """
\"\"\"
Migration script for version {version}.
Description: {description}
\"\"\"

def upgrade(data: dict) -> dict:
    \"\"\"
    Applies the upgrade logic to the data.
    \"\"\"
    # --- Implement your migration logic here ---

    # Example:
    # if 'old_field' in data:
    #     data['new_field'] = data.pop('old_field')

    print(f"  Successfully applied migration to version {version}.")
    return data
"""

def create_migration_script(description: str) -> str:
    """Creates a new, timestamped migration script."""
    if not os.path.exists(MIGRATION_DIR):
        os.makedirs(MIGRATION_DIR)

    existing_migrations = sorted([f for f in os.listdir(MIGRATION_DIR) if f.startswith('v_')])
    latest_version = 0
    if existing_migrations:
        latest_version = int(existing_migrations[-1].split('_')[1])

    new_version = latest_version + 1
    sanitized_description = re.sub(r'[^a-zA-Z0-9_]', '', description.lower().replace(' ', '_'))

    script_name = f"v_{new_version:03d}_{sanitized_description}.py"
    script_path = os.path.join(MIGRATION_DIR, script_name)

    with open(script_path, 'w') as f:
        f.write(MIGRATION_TEMPLATE.format(version=new_version, description=description))

    print(f"Created new migration script: {script_path}")
    return script_path


def discover_migrations() -> List[Tuple[int, Callable]]:
    """Discovers and loads migration functions from the migrations directory."""
    migrations = []
    if not os.path.exists(MIGRATION_DIR):
        return []

    for filename in sorted(os.listdir(MIGRATION_DIR)):
        if filename.startswith('v_') and filename.endswith('.py'):
            match = re.match(r'v_(\d+)_.*\.py', filename)
            if not match:
                continue

            version = int(match.group(1))
            module_name = f"migrations.{filename[:-3]}"
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(MIGRATION_DIR, filename))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'upgrade'):
                migrations.append((version, getattr(module, 'upgrade')))

    return migrations

def migrate_data(data: Dict[str, Any], target_version: int = -1) -> Dict[str, Any]:
    """
    Applies migrations to bring data to the target version.
    If target_version is -1, migrates to the latest version available.
    """
    current_version = data.get('schema_version', 0)

    all_migrations = discover_migrations()

    if target_version == -1 and all_migrations:
        target_version = all_migrations[-1][0]

    if current_version >= target_version:
        print("Data is already at or beyond the target version. No migration needed.")
        return data

    migrated_data = data.copy()
    for version, upgrade_func in all_migrations:
        if version > current_version and version <= target_version:
            print(f"Applying migration for version {version}...")
            migrated_data = upgrade_func(migrated_data)
            migrated_data['schema_version'] = version

    return migrated_data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="QuantaCirc Migration Tool")
    parser.add_argument("command", choices=["migrate", "create"], help="Command to execute.")
    parser.add_argument("--description", help="Description for a new migration script.")

    args = parser.parse_args()

    if args.command == "create":
        if not args.description:
            print("Error: --description is required for the 'create' command.")
        else:
            create_migration_script(args.description)

    elif args.command == "migrate":
        # Example Usage
        print("--- Running Migration ---")

        import shutil
        # Clean up migrations dir before running for a clean test
        if os.path.exists(MIGRATION_DIR):
            shutil.rmtree(MIGRATION_DIR)

        # Create dummy migration files for the example
        script_1_path = create_migration_script("rename_name_field")
        with open(script_1_path, "w") as f:
            f.write("""
def upgrade(data):
    print("  -> Running rename_name_field migration")
    if 'name' in data:
        full_name = data.pop('name', '').split(' ', 1)
        data['first_name'] = full_name[0]
        data['last_name'] = full_name[1] if len(full_name) > 1 else ''
    return data
""")

        script_2_path = create_migration_script("add_status_field")
        with open(script_2_path, "w") as f:
            f.write("""
def upgrade(data):
    print("  -> Running add_status_field migration")
    data['status'] = data.get('status', 'active')
    return data
""")

        # Sample data from an older version (v0)
        v0_data = {
            "schema_version": 0,
            "name": "John Doe",
            "email": "john.doe@example.com"
        }

        print(f"Original V0 data: {v0_data}")

        # Migrate the data to the latest version
        migrated_data = migrate_data(v0_data)
        print(f"Migrated data: {migrated_data}")

        # Clean up dummy files and directory
        shutil.rmtree(MIGRATION_DIR)
