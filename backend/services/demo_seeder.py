"""Demo project auto-seeder for Shipcheck zero-friction trial mode."""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

from backend.database.schema import get_db, get_project_dir
from backend.services.scanner import ScannerService

DEMO_PROJECT_ID = "demo-sample-id"
DEMO_PROJECT_NAME = "E-Commerce Web API (Sample)"
DEMO_SCAN_ID = "demo-scan-001"


async def ensure_demo_project() -> dict:
    """Ensure the sample project is populated on disk and in database with full audit results."""
    import sys
    if getattr(sys, "frozen", False):
        root_dir = Path(getattr(sys, "_MEIPASS", os.path.dirname(__file__)))
    else:
        root_dir = Path(__file__).resolve().parent.parent.parent
    sample_src = root_dir / "sample_vulnerable_app"
    demo_dir = get_project_dir(DEMO_PROJECT_ID)

    # 1. Ensure project files exist on disk
    if not demo_dir.exists() or not (demo_dir / "app.py").exists():
        demo_dir.mkdir(parents=True, exist_ok=True)
        if sample_src.exists():
            for item in sample_src.iterdir():
                dest = demo_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)

    # 2. Check if project row exists and has findings
    needs_scan = False
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, security_score FROM projects WHERE id = ?", (DEMO_PROJECT_ID,))
        row = cursor.fetchone()
        if not row:
            project_context = {
                "framework": "flask",
                "language": "python",
                "database": "sqlite",
                "features": ["auth", "ecommerce", "payment_flow"],
                "is_sample": True
            }
            cursor.execute("""
                INSERT INTO projects (id, name, created_at, project_context, sentinel_enabled)
                VALUES (?, ?, ?, ?, 1)
            """, (DEMO_PROJECT_ID, DEMO_PROJECT_NAME, datetime.utcnow().isoformat(), json.dumps(project_context)))
            needs_scan = True
        elif row[1] is None:
            needs_scan = True

        cursor.execute("SELECT COUNT(*) FROM findings WHERE scan_id IN (SELECT id FROM scans WHERE project_id = ?)", (DEMO_PROJECT_ID,))
        count = cursor.fetchone()[0]
        if count == 0:
            needs_scan = True

    # 3. If needed, execute full scanner
    if needs_scan:
        scanner = ScannerService(str(demo_dir), DEMO_PROJECT_ID, DEMO_SCAN_ID)
        report = await scanner.run_scan()
        return {
            "status": "seeded",
            "project_id": DEMO_PROJECT_ID,
            "findings_count": report.get("summary", {}).get("total_findings", 0)
        }

    return {
        "status": "already_seeded",
        "project_id": DEMO_PROJECT_ID
    }
