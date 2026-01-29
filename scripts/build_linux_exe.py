#!/usr/bin/env python3
"""
Build Linux executable for SpellEngine / Dread Citadel

This script prepares and builds a Linux binary using PyInstaller.

REQUIREMENTS (install on Linux):
    pip install pyinstaller pygame pyyaml pydantic rich psutil

USAGE:
    python scripts/build_linux_exe.py

The resulting DreadCitadel binary will be in the dist/ folder.

NOTE: This must be run on Linux. PyInstaller does not support cross-compilation.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
SPEC_FILE = PROJECT_ROOT / "spellengine_linux.spec"
DIST_DIR = PROJECT_ROOT / "dist"


def check_platform():
    """Verify we're running on Linux."""
    if sys.platform != "linux":
        print("=" * 60)
        print("  WARNING: This script should be run on Linux!")
        print("=" * 60)
        print()
        print("PyInstaller cannot cross-compile Linux executables.")
        print()

        response = input("Continue anyway for testing? [y/N]: ").strip().lower()
        if response != "y":
            sys.exit(1)
        print()


def check_dependencies():
    """Verify required packages are installed."""
    # Map package names to their import names
    required = {
        "pyinstaller": "PyInstaller",
        "pygame": "pygame",
        "pyyaml": "yaml",
        "psutil": "psutil",
        "pydantic": "pydantic",
        "rich": "rich",
    }
    missing = []

    for pkg_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print("Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print()
        print("Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build...")

    # Clean PyInstaller build cache
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print(f"  Removed: {build_dir}")

    # Clean dist directory (but keep other releases)
    exe_path = DIST_DIR / "DreadCitadel"
    if exe_path.exists():
        exe_path.unlink()
        print(f"  Removed: {exe_path}")

    # Clean __pycache__ directories
    for pycache in PROJECT_ROOT.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)

    print()


def run_pyinstaller():
    """Run PyInstaller to build the executable."""
    print("Building Linux executable with PyInstaller...")
    print(f"  Spec file: {SPEC_FILE}")
    print()

    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE),
    ]

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        print()
        print("ERROR: PyInstaller build failed!")
        sys.exit(1)


def verify_build():
    """Verify the build succeeded."""
    exe_path = DIST_DIR / "DreadCitadel"

    if not exe_path.exists():
        print(f"ERROR: Expected output not found: {exe_path}")
        sys.exit(1)

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print()
    print("=" * 60)
    print("  BUILD SUCCESSFUL!")
    print("=" * 60)
    print()
    print(f"  Executable: {exe_path}")
    print(f"  Size: {size_mb:.1f} MB")
    print()
    print("  The executable includes all dependencies and assets.")
    print("  Run with: ./DreadCitadel")
    print()


def create_release_package():
    """Create a release package with README."""
    print("Creating release package...")

    release_dir = DIST_DIR / "DreadCitadel-Linux"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)

    # Copy executable
    exe_src = DIST_DIR / "DreadCitadel"
    exe_dst = release_dir / "DreadCitadel"
    shutil.copy2(exe_src, exe_dst)

    # Make executable
    os.chmod(exe_dst, 0o755)

    # Create README
    readme_content = """# Dread Citadel - Linux Edition

## How to Play

1. Make executable: chmod +x DreadCitadel
2. Run: ./DreadCitadel
3. No installation required!

## Requirements

- Linux x86_64 (Ubuntu 20.04+, Kali, etc.)
- SDL2 libraries (usually pre-installed)

If you get audio errors, install:
    sudo apt install libsdl2-mixer-2.0-0

## About

Dread Citadel is an educational adventure game that teaches password security
concepts through interactive gameplay. Break into the fortress by cracking
increasingly difficult password hashes!

## Controls

- Mouse: Click buttons and UI elements
- Keyboard: Type password guesses
- ESC: Return to title screen
- F12: Take screenshot

## Observer Mode

If you don't have hashcat or john installed, the game runs in Observer Mode
where hints reveal the answers. This lets you experience the story without
the cracking tools.

## For Full Experience

Install hashcat: sudo apt install hashcat
Install john: sudo apt install john

## Credits

Created by The Cipher Circle
A human-AI collaborative project

## License

Proprietary - All Rights Reserved
"""

    readme_path = release_dir / "README.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"  Created: {release_dir}")
    print(f"  Contents: DreadCitadel, README.txt")

    # Create tarball
    tar_path = DIST_DIR / "DreadCitadel-Linux.tar.gz"
    if tar_path.exists():
        tar_path.unlink()

    print(f"  Creating: {tar_path}")
    shutil.make_archive(
        str(DIST_DIR / "DreadCitadel-Linux"),
        "gztar",
        str(release_dir.parent),
        release_dir.name,
    )

    print()
    print(f"  Release package: {tar_path}")
    print()


def main():
    """Main build process."""
    print()
    print("=" * 60)
    print("  SpellEngine / Dread Citadel - Linux Build")
    print("=" * 60)
    print()

    check_platform()
    check_dependencies()
    clean_build()
    run_pyinstaller()
    verify_build()
    create_release_package()

    print("Done!")
    print()


if __name__ == "__main__":
    main()
