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

# A registry of migration functions.
# The key is the target version number.
MIGRATION_REGISTRY: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

def register_migration(version: int):
    """Decorator to register a migration function for a specific version."""
    def decorator(func: Callable):
        MIGRATION_REGISTRY[version] = func
        return func
    return decorator

def migrate_data(data: Dict[str, Any], current_version: int, target_version: int) -> Dict[str, Any]:
    """
    Applies migrations to bring data from a current version to a target version.
    """
    if current_version >= target_version:
        print("Data is already at or beyond the target version. No migration needed.")
        return data

    # Apply migrations sequentially
    migrated_data = data.copy()
    for v in sorted(MIGRATION_REGISTRY.keys()):
        if v > current_version and v <= target_version:
            print(f"Applying migration for version {v}...")
            migration_func = MIGRATION_REGISTRY[v]
            migrated_data = migration_func(migrated_data)

    migrated_data['schema_version'] = target_version
    return migrated_data

# --- Example Migrations ---

@register_migration(version=2)
def from_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example migration: Converts a simple 'name' field to 'first_name', 'last_name'.
    """
    if 'name' in data:
        full_name = data.pop('name', '').split(' ', 1)
        data['first_name'] = full_name[0]
        data['last_name'] = full_name[1] if len(full_name) > 1 else ''
    return data

@register_migration(version=3)
def from_v2_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example migration: Adds a new 'status' field with a default value.
    """
    data['status'] = data.get('status', 'active')
    return data


if __name__ == '__main__':
    # Example Usage
    print("--- Migration Tool Example ---")

    # Sample data from an older version (v1)
    v1_data = {
        "schema_version": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }

    print(f"Original V1 data: {v1_data}")

    # Migrate the data to the latest version (v3)
    migrated_v3_data = migrate_data(v1_data, current_version=1, target_version=3)

    print(f"Migrated V3 data: {migrated_v3_data}")
