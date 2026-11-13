"""PyInstaller specification and build script for Vibeflare Lite executable."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable


def build():
    print("[*] Starting Vibeflare Lite binary compilation...")

    frontend_dir = ROOT_DIR / "frontend"
    native_dir = ROOT_DIR / "backend" / "native"
    sample_dir = ROOT_DIR / "sample_vulnerable_app"

    # Build PyInstaller command line arguments
    cmd = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--name=VibeflareLite",
        "--noconfirm",
        "--onedir",
        "--console",
        "--add-data", f"{frontend_dir};frontend",
    ]

    if sample_dir.exists():
        cmd.extend(["--add-data", f"{sample_dir};sample_vulnerable_app"])

    if native_dir.exists():
        cmd.extend(["--add-data", f"{native_dir};backend/native"])

    # Hidden imports
    hidden_imports = [
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "fastapi",
        "fastapi.staticfiles",
        "fastapi.responses",
        "fastapi.middleware.cors",
        "sqlite3",
        "json",
        "pydantic",
        "aiofiles",
        "backend",
        "backend.main",
        "backend.database",
        "backend.database.schema",
        "backend.models",
        "backend.models.schemas",
        "backend.services",
        "backend.services.scanner",
        "backend.services.llm",
        "backend.services.workspace",
        "backend.services.ai_cache",
        "backend.services.remediation",
        "backend.services.sandbox",
        "backend.services.demo_seeder",
        "backend.services.native_inspector",
        "backend.services.project_detector",
        "backend.services.secure_extract",
        "backend.services.context_window",
        "backend.services.fix_synthesis",
        "backend.services.runtime_monitoring",
        "backend.services.sentinel_integration",
        "backend.api",
        "backend.api.projects",
        "backend.api.scans",
        "backend.api.reports",
        "backend.api.runtime",
        "backend.api.proxy",
        "backend.api.fixes",
        "backend.api.sentinel",
        "backend.api.sandbox",
        "backend.api.remediation",
        "backend.api.settings",
        "backend.scanners",
        "backend.scanners.security",
        "backend.scanners.privacy",
        "backend.scanners.reliability",
        "backend.scanners.production",
        "backend.scanners.dependency",
        "backend.scanners.configuration",
        "backend.scanners.runtime",
        "sentinel_rasp",
        "sentinel_rasp.core",
        "sentinel_rasp.python",
        "sentinel_rasp.python.sentinel",
        "sentinel_rasp.python.sentinel.engine",
        "sentinel_rasp.python.sentinel.runtime",
        "sentinel_rasp.python.sentinel.policy",
        "sentinel_rasp.python.sentinel.events",
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    cmd.append(str(ROOT_DIR / "launcher.py"))

    print(f"[*] Executing command:\n{' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode == 0:
        dist_dir = ROOT_DIR / "dist" / "VibeflareLite"
        zip_out = ROOT_DIR / "dist" / "vibeflare-lite-v1.0.0-windows-x64"
        print(f"\n[*] Creating compressed release archive: {zip_out}.zip ...")
        shutil.make_archive(str(zip_out), 'zip', root_dir=str(ROOT_DIR / "dist"), base_dir="VibeflareLite")
        print("\n=======================================================")
        print(" [OK] Build completed successfully!")
        print(f" [OK] Directory: {dist_dir}")
        print(f" [OK] Standalone Executable: {dist_dir / 'VibeflareLite.exe'}")
        print(f" [OK] Release Archive: {zip_out}.zip")
        print("=======================================================\n")
    else:
        print(f"\n[X] Build failed with exit code: {res.returncode}")
        sys.exit(res.returncode)


if __name__ == "__main__":
    build()
