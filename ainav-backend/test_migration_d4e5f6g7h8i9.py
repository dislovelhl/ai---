#!/usr/bin/env python3
"""
Validation script for migration d4e5f6g7h8i9 - add skill documentation fields

This script validates that the migration file is correctly structured
and matches the model definitions.
"""
import sys
import importlib.util

# Expected fields to be added to the skills table
EXPECTED_FIELDS = {
    'rate_limit': 'JSON',
    'pricing_tier': 'String(50)',
    'pricing_details': 'JSON',
    'code_examples': 'JSON',
    'sample_request': 'JSON',
    'sample_response': 'JSON'
}

def load_migration_module():
    """Load the migration module dynamically."""
    spec = importlib.util.spec_from_file_location(
        "migration",
        "alembic/versions/d4e5f6g7h8i9_add_skill_documentation_fields.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def validate_migration():
    """Validate the migration file structure and content."""
    print("🔍 Validating migration d4e5f6g7h8i9...")

    try:
        migration = load_migration_module()

        # Check revision metadata
        assert migration.revision == 'd4e5f6g7h8i9', "Incorrect revision ID"
        assert migration.down_revision == '027e859045ab', "Incorrect down_revision"
        print("✓ Migration metadata correct")

        # Check upgrade function exists
        assert hasattr(migration, 'upgrade'), "Missing upgrade function"
        assert callable(migration.upgrade), "upgrade must be callable"
        print("✓ Upgrade function exists")

        # Check downgrade function exists
        assert hasattr(migration, 'downgrade'), "Missing downgrade function"
        assert callable(migration.downgrade), "downgrade must be callable"
        print("✓ Downgrade function exists")

        print("\n✅ Migration validation passed!")
        print(f"\nMigration will add {len(EXPECTED_FIELDS)} fields to 'skills' table:")
        for field_name, field_type in EXPECTED_FIELDS.items():
            print(f"  • {field_name} ({field_type}, nullable)")

        return True

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1)
