#!/usr/bin/env python3
"""
Pre-migration hook to automatically backup courses before migrations
Run this before any alembic migration
"""

import subprocess
import sys
from backup_courses import backup_courses

def main():
    print("🔄 Pre-migration backup running...")
    if backup_courses():
        print("✅ Backup complete, safe to run migrations")
        return 0
    else:
        print("❌ Backup failed, aborting migration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
