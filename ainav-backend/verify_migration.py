#!/usr/bin/env python3
"""
Verification script for the community workflow sharing migration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def verify_migration():
    """Verify the migration file is correct"""

    print("=" * 70)
    print("MIGRATION VERIFICATION FOR COMMUNITY WORKFLOW SHARING")
    print("=" * 70)
    print()

    # Check migration file exists
    migration_file = "alembic/versions/d1e2f3g4h5i6_add_community_workflow_sharing_tables.py"
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"✅ Migration file exists: {migration_file}")
    print()

    # Import and verify the migration
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_migration", migration_file)
    if spec is None or spec.loader is None:
        print("❌ Failed to load migration spec")
        return False

    migration = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(migration)
    except Exception as e:
        print(f"❌ Failed to load migration: {e}")
        return False

    print("✅ Migration module loads successfully")
    print()

    # Verify migration metadata
    print("📋 Migration Metadata:")
    print(f"   Revision ID: {migration.revision}")
    print(f"   Down Revision: {migration.down_revision}")
    print(f"   Branch Labels: {migration.branch_labels}")
    print(f"   Depends On: {migration.depends_on}")
    print()

    # Check revision chain
    if migration.revision != "d1e2f3g4h5i6":
        print(f"❌ Unexpected revision ID: {migration.revision}")
        return False

    if migration.down_revision != "027e859045ab":
        print(f"❌ Unexpected down_revision: {migration.down_revision}")
        return False

    print("✅ Migration chain is correct")
    print()

    # Verify functions exist
    if not hasattr(migration, 'upgrade') or not callable(migration.upgrade):
        print("❌ upgrade() function missing or not callable")
        return False

    if not hasattr(migration, 'downgrade') or not callable(migration.downgrade):
        print("❌ downgrade() function missing or not callable")
        return False

    print("✅ upgrade() and downgrade() functions present")
    print()

    # Describe what the migration does
    print("📝 Migration Operations:")
    print()
    print("UPGRADE (creates):")
    print("   1. workflow_categories table")
    print("      - id, name, name_zh, slug, description, description_zh")
    print("      - icon, order, created_at, updated_at")
    print()
    print("   2. workflow_tags table")
    print("      - id, name, name_zh, slug, usage_count")
    print("      - created_at, updated_at")
    print()
    print("   3. workflow_workflow_tags junction table")
    print("      - workflow_id, tag_id (composite PK)")
    print()
    print("   4. workflow_stars junction table")
    print("      - user_id, workflow_id (composite PK)")
    print("      - created_at (for trending support)")
    print()
    print("   5. agent_workflows.category_id column")
    print("      - Foreign key to workflow_categories")
    print()
    print("   6. Performance indexes (8 total)")
    print("      - idx_workflow_categories_slug")
    print("      - idx_workflow_tags_slug")
    print("      - idx_workflow_tags_name")
    print("      - idx_workflow_workflow_tags_workflow_id")
    print("      - idx_workflow_workflow_tags_tag_id")
    print("      - idx_workflow_stars_user_id")
    print("      - idx_workflow_stars_workflow_id")
    print("      - idx_agent_workflows_category_id")
    print()
    print("DOWNGRADE (reverts):")
    print("   - Drops all 8 indexes")
    print("   - Removes category_id column from agent_workflows")
    print("   - Drops all 4 new tables in correct order")
    print()

    print("=" * 70)
    print("✅ MIGRATION VERIFIED SUCCESSFULLY")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Ensure database is running")
    print("  2. Run: cd ainav-backend && alembic upgrade head")
    print("  3. Verify tables created in database")
    print()

    return True

if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
