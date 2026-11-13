"""Clear all cached scans, findings, projects, and AI cache in Shipcheck."""

import os
import shutil
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATHS = [
    ROOT_DIR / "shipcheck.db",
    ROOT_DIR / "backend" / "shipcheck.db",
    ROOT_DIR / "dist" / "shipcheck.db",
]

PROJECT_DIRS = [
    ROOT_DIR / "projects",
    ROOT_DIR / "dist" / "projects",
]

TABLES_TO_CLEAR = [
    "ai_analysis_cache",
    "remediation_verifications",
    "remediation_proposals",
    "fix_validations",
    "findings",
    "scans",
    "dependencies",
    "projects",
]


def clear_databases():
    """Clear all records from database tables."""
    cleared = 0
    for db_path in DB_PATHS:
        if not db_path.exists():
            continue
        print(f"[*] Clearing database: {db_path}")
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")
            for table in TABLES_TO_CLEAR:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            cursor.execute("VACUUM")
            conn.close()
            cleared += 1
            print(f"    [OK] Cleared tables in {db_path}")
        except Exception as e:
            print(f"    [!] Error clearing {db_path}: {e}")
    return cleared


def clear_project_directories():
    """Clear uploaded/extracted project folders while preserving directory structure."""
    removed = 0
    for pdir in PROJECT_DIRS:
        if not pdir.exists():
            continue
        print(f"[*] Cleaning projects directory: {pdir}")
        for item in pdir.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    removed += 1
                elif item.is_file():
                    item.unlink()
                    removed += 1
            except Exception as e:
                print(f"    [!] Error removing {item}: {e}")
    return removed


def clear_pycache():
    """Recursively remove __pycache__ directories and .pyc files."""
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".venv" in root:
            continue
        for d in dirs:
            if d == "__pycache__":
                full_path = Path(root) / d
                try:
                    shutil.rmtree(full_path)
                    count += 1
                except Exception:
                    pass
    return count


def main():
    print("=" * 60)
    print(" Shipcheck Cache & Data Cleaner")
    print("=" * 60)
    db_count = clear_databases()
    proj_count = clear_project_directories()
    pyc_count = clear_pycache()
    print("-" * 60)
    print(f" Summary: {db_count} DBs cleared, {proj_count} project items removed, {pyc_count} pycache dirs removed.")
    print(" Done!")


if __name__ == "__main__":
    main()
