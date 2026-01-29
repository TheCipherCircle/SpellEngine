#!/usr/bin/env python3
"""
Build and package SpellEngine/Dread Citadel for distribution.

Creates a clean release package with:
- Version manifest with SHA256 checksums
- No dev files (.git, __pycache__, etc.)
- Optional auto-copy to Proton Drive sync folder

Usage:
    python scripts/build_release.py
    python scripts/build_release.py --version 0.9.1
    python scripts/build_release.py --proton-sync ~/ProtonDrive/SpellEngine-Releases
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Files/folders to EXCLUDE from release
EXCLUDE_PATTERNS = [
    '.git',
    '.gitignore',
    '.claude',
    '.patternforge',
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.DS_Store',
    '.env',
    '.venv',
    'venv',
    'env',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'scripts/build_release.py',  # Don't include the build script itself
    'tests',
    '*.egg-info',
    'dist',
    'build',
    '.coverage',
    'htmlcov',
    'mirth',  # Dev tooling
    'scribe',  # Dev tooling
    'cipher-circle',  # Internal docs
    'assets/images/review',  # Review assets
]

# Files to ALWAYS include
REQUIRED_FILES = [
    'pyproject.toml',
    'README.md',
    'TESTER_QUICKSTART.md',
    'install.sh',
    'spellengine',
    'assets',
    'content',
    'lore',
    'docs',
]


def get_git_info() -> dict:
    """Get current git commit info."""
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        commit_short = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # Check for uncommitted changes
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        dirty = bool(status)

        return {
            'commit': commit,
            'commit_short': commit_short,
            'branch': branch,
            'dirty': dirty
        }
    except subprocess.CalledProcessError:
        return {
            'commit': 'unknown',
            'commit_short': 'unknown',
            'branch': 'unknown',
            'dirty': True
        }


def sha256_file(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def should_exclude(path: Path, base: Path) -> bool:
    """Check if a path should be excluded from the release."""
    rel_path = path.relative_to(base)
    rel_str = str(rel_path)

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # Wildcard pattern
            if rel_str.endswith(pattern[1:]):
                return True
        elif pattern in rel_path.parts:
            # Directory or file name match
            return True
        elif rel_str == pattern:
            # Exact match
            return True

    return False


def copy_tree_filtered(src: Path, dst: Path, base: Path) -> list:
    """Copy directory tree, excluding unwanted files. Returns list of copied files."""
    copied_files = []

    if src.is_file():
        if not should_exclude(src, base):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied_files.append(dst)
    elif src.is_dir():
        if not should_exclude(src, base):
            for item in src.iterdir():
                rel = item.relative_to(src)
                copied_files.extend(copy_tree_filtered(item, dst / rel, base))

    return copied_files


def build_release(version: str = None, proton_sync_path: Path = None) -> Path:
    """Build a release package."""

    # Get git info
    git_info = get_git_info()

    # Determine version
    if not version:
        # Try to get from pyproject.toml or use git info
        version = f"0.9.0-{git_info['commit_short']}"

    if git_info['dirty']:
        version += '-dirty'
        print(f"WARNING: Working directory has uncommitted changes!")

    # Create build directory
    build_time = datetime.now(timezone.utc)
    build_name = f"spellengine-{version}"
    build_dir = PROJECT_ROOT / 'dist' / build_name

    # Clean previous build
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    print(f"Building release: {build_name}")
    print(f"  Git commit: {git_info['commit_short']} ({git_info['branch']})")
    print(f"  Build time: {build_time.isoformat()}Z")
    print()

    # Copy files
    print("Copying files...")
    all_files = []
    for item in REQUIRED_FILES:
        src = PROJECT_ROOT / item
        if src.exists():
            dst = build_dir / item
            copied = copy_tree_filtered(src, dst, PROJECT_ROOT)
            all_files.extend(copied)
            print(f"  {item}: {len(copied)} files")
        else:
            print(f"  {item}: MISSING (skipped)")

    # Calculate checksums
    print("\nCalculating checksums...")
    checksums = {}
    for filepath in all_files:
        rel_path = filepath.relative_to(build_dir)
        checksums[str(rel_path)] = sha256_file(filepath)

    # Create manifest
    manifest = {
        'name': 'SpellEngine - The Dread Citadel',
        'version': version,
        'build_time': build_time.isoformat() + 'Z',
        'git': git_info,
        'file_count': len(all_files),
        'checksums': checksums
    }

    manifest_path = build_dir / 'BUILD_MANIFEST.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest: {manifest_path.name}")

    # Create verification script
    verify_script = build_dir / 'verify_build.py'
    with open(verify_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Verify this build's integrity against the manifest."""
import hashlib
import json
import sys
from pathlib import Path

def sha256_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def main():
    root = Path(__file__).parent
    manifest_path = root / 'BUILD_MANIFEST.json'

    if not manifest_path.exists():
        print("ERROR: BUILD_MANIFEST.json not found!")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    print(f"Verifying: {manifest['name']} v{manifest['version']}")
    print(f"Built: {manifest['build_time']}")
    print(f"Commit: {manifest['git']['commit_short']}")
    print()

    errors = []
    for rel_path, expected_hash in manifest['checksums'].items():
        filepath = root / rel_path
        if not filepath.exists():
            errors.append(f"MISSING: {rel_path}")
        else:
            actual_hash = sha256_file(filepath)
            if actual_hash != expected_hash:
                errors.append(f"MODIFIED: {rel_path}")

    if errors:
        print("VERIFICATION FAILED!")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print(f"VERIFIED: All {len(manifest['checksums'])} files match checksums.")
        sys.exit(0)

if __name__ == '__main__':
    main()
''')
    print(f"  Verification script: {verify_script.name}")

    # Create zip
    print("\nCreating zip archive...")
    zip_path = PROJECT_ROOT / 'dist' / f'{build_name}.zip'
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for filepath in build_dir.rglob('*'):
            if filepath.is_file():
                arcname = filepath.relative_to(build_dir.parent)
                zf.write(filepath, arcname)

    zip_hash = sha256_file(zip_path)
    print(f"  Archive: {zip_path.name}")
    print(f"  SHA256: {zip_hash}")

    # Write zip hash to sidecar file
    hash_file = zip_path.with_suffix('.zip.sha256')
    with open(hash_file, 'w') as f:
        f.write(f"{zip_hash}  {zip_path.name}\n")
    print(f"  Hash file: {hash_file.name}")

    # Copy to Proton Drive sync folder if specified
    if proton_sync_path:
        proton_sync_path = Path(proton_sync_path).expanduser()
        if proton_sync_path.exists():
            print(f"\nSyncing to Proton Drive: {proton_sync_path}")
            shutil.copy2(zip_path, proton_sync_path / zip_path.name)
            shutil.copy2(hash_file, proton_sync_path / hash_file.name)

            # Write latest version pointer
            latest_file = proton_sync_path / 'LATEST.txt'
            with open(latest_file, 'w') as f:
                f.write(f"{zip_path.name}\n")
                f.write(f"SHA256: {zip_hash}\n")
                f.write(f"Built: {build_time.isoformat()}Z\n")
                f.write(f"Commit: {git_info['commit_short']}\n")
            print(f"  Updated LATEST.txt")
            print("  Files will sync automatically via Proton Drive")
        else:
            print(f"\nWARNING: Proton Drive path not found: {proton_sync_path}")
            print("  Skipping sync. Create the folder or check the path.")

    print(f"\n{'='*50}")
    print(f"BUILD COMPLETE: {build_name}")
    print(f"{'='*50}")
    print(f"\nDistribution package: {zip_path}")
    print(f"Verify with: shasum -a 256 -c {hash_file.name}")

    return zip_path


def main():
    parser = argparse.ArgumentParser(description='Build SpellEngine release package')
    parser.add_argument('--version', '-v', help='Version string (default: auto from git)')
    parser.add_argument('--proton-sync', '-p', help='Proton Drive sync folder path')

    args = parser.parse_args()

    build_release(
        version=args.version,
        proton_sync_path=args.proton_sync
    )


if __name__ == '__main__':
    main()
