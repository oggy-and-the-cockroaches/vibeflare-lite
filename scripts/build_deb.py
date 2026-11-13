"""Debian (.deb) Package Builder for Vibeflare Lite."""

import os
import io
import time
import tarfile
import gzip
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def create_tar_gz(files_dict):
    """Create in-memory .tar.gz from dictionary of {relative_path: (content_bytes, mode)}."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for path, (data, mode) in files_dict.items():
            ti = tarfile.TarInfo(name=path)
            ti.size = len(data)
            ti.mtime = int(time.time())
            ti.mode = mode
            ti.uname = "root"
            ti.gname = "root"
            ti.uid = 0
            ti.gid = 0
            tar.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def create_ar_member(name, data):
    """Format single entry for ar archive."""
    header = f"{name:<16}{int(time.time()):<12}0     0     100644  {len(data):<10}`\n".encode("ascii")
    padding = b"\n" if len(data) % 2 != 0 else b""
    return header + data + padding


def build_deb_package(output_path: Path):
    """Construct complete .deb binary package."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. debian-binary
    debian_binary = b"2.0\n"

    # 2. control.tar.gz
    control_content = """Package: vibeflare-lite
Version: 1.0.0
Section: devel
Priority: optional
Architecture: amd64
Maintainer: Vibeflare Security Team
Description: Vibeflare Lite - Community Desktop Security & Mock Port Shield
 Local, zero-configuration application security scanner, offline AI remediation
 engine, and real-time mock port WAF reverse proxy.
""".encode("utf-8")

    control_files = {"./control": (control_content, 0o644)}
    control_tar_gz = create_tar_gz(control_files)

    # 3. data.tar.gz
    launcher_script = """#!/bin/bash
set -e
exec python3 -m backend.main "$@"
""".encode("utf-8")

    desktop_file = """[Desktop Entry]
Name=Vibeflare Lite
Comment=Application Security & Mock Port Shield
Exec=/usr/local/bin/vibeflare-lite
Icon=security-high
Terminal=true
Type=Application
Categories=Development;Security;
""".encode("utf-8")

    data_files = {
        "./usr/local/bin/vibeflare-lite": (launcher_script, 0o755),
        "./usr/share/applications/vibeflare-lite.desktop": (desktop_file, 0o644),
    }
    data_tar_gz = create_tar_gz(data_files)

    # Assemble .deb file (ar archive)
    ar_magic = b"!<arch>\n"
    deb_bytes = (
        ar_magic
        + create_ar_member("debian-binary", debian_binary)
        + create_ar_member("control.tar.gz", control_tar_gz)
        + create_ar_member("data.tar.gz", data_tar_gz)
    )

    with open(output_path, "wb") as f:
        f.write(deb_bytes)

    print(f"[SUCCESS] Built Debian package: {output_path} ({len(deb_bytes):,} bytes)")


if __name__ == "__main__":
    out = ROOT_DIR / "dist" / "vibeflare-lite_1.0.0_amd64.deb"
    build_deb_package(out)
