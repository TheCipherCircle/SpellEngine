"""
Tool Installer for SpellEngine

Downloads and installs hashcat/john for users who don't have them.
Provides a seamless onboarding experience.

PROPRIETARY - All Rights Reserved
Copyright (c) 2026 The Cipher Circle
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve


# Tool download URLs by platform
HASHCAT_URLS = {
    "Windows": "https://hashcat.net/files/hashcat-6.2.6.7z",
    "Darwin": None,  # Use homebrew
    "Linux": None,   # Use package manager
}

JOHN_URLS = {
    "Windows": "https://www.openwall.com/john/k/john-1.9.0-jumbo-1-win64.zip",
    "Darwin": None,  # Use homebrew
    "Linux": None,   # Use package manager
}


def get_tools_dir() -> Path:
    """Get the directory where tools are stored."""
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / "SpellEngine" / "tools"
    else:
        return Path.home() / ".spellengine" / "tools"


def get_hashcat_path() -> Optional[Path]:
    """Get path to hashcat if installed in tools dir."""
    tools_dir = get_tools_dir()
    if platform.system() == "Windows":
        hashcat_exe = tools_dir / "hashcat" / "hashcat.exe"
        if hashcat_exe.exists():
            return hashcat_exe
    return None


def get_john_path() -> Optional[Path]:
    """Get path to john if installed in tools dir."""
    tools_dir = get_tools_dir()
    if platform.system() == "Windows":
        john_exe = tools_dir / "john" / "run" / "john.exe"
        if john_exe.exists():
            return john_exe
    return None


def download_with_progress(url: str, dest: Path, label: str = "Downloading") -> bool:
    """Download a file with progress indication."""
    try:
        print(f"{label}...")

        def progress_hook(count, block_size, total_size):
            if total_size > 0:
                percent = min(100, count * block_size * 100 // total_size)
                bar = "=" * (percent // 5) + " " * (20 - percent // 5)
                print(f"\r  [{bar}] {percent}%", end="", flush=True)

        urlretrieve(url, dest, reporthook=progress_hook)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n  Error: {e}")
        return False


def extract_archive(archive_path: Path, dest_dir: Path) -> bool:
    """Extract zip or 7z archive."""
    try:
        print(f"  Extracting to {dest_dir}...")

        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(dest_dir)
            return True
        elif archive_path.suffix == ".7z":
            # Try 7z command
            result = subprocess.run(
                ["7z", "x", str(archive_path), f"-o{dest_dir}", "-y"],
                capture_output=True
            )
            return result.returncode == 0
        else:
            print(f"  Unknown archive format: {archive_path.suffix}")
            return False
    except Exception as e:
        print(f"  Extraction error: {e}")
        return False


def install_hashcat_windows() -> Optional[Path]:
    """Download and install hashcat on Windows."""
    tools_dir = get_tools_dir()
    hashcat_dir = tools_dir / "hashcat"

    # Check if already installed
    if (hashcat_dir / "hashcat.exe").exists():
        print("  hashcat already installed.")
        return hashcat_dir / "hashcat.exe"

    print()
    print("Installing hashcat for Windows...")

    # Create tools directory
    tools_dir.mkdir(parents=True, exist_ok=True)

    # Download
    url = HASHCAT_URLS["Windows"]
    if not url:
        print("  No download URL available.")
        return None

    # Use zip version instead of 7z for easier extraction
    zip_url = url.replace(".7z", ".zip")

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / "hashcat.zip"

        if not download_with_progress(zip_url, archive_path, "  Downloading hashcat"):
            # Try 7z version
            archive_path = Path(tmpdir) / "hashcat.7z"
            if not download_with_progress(url, archive_path, "  Trying 7z version"):
                return None

        # Extract
        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir()

        if not extract_archive(archive_path, extract_dir):
            return None

        # Find extracted folder (usually hashcat-x.x.x)
        extracted = list(extract_dir.iterdir())
        if not extracted:
            print("  No files extracted.")
            return None

        src_dir = extracted[0]

        # Move to tools dir
        if hashcat_dir.exists():
            shutil.rmtree(hashcat_dir)
        shutil.move(str(src_dir), str(hashcat_dir))

    hashcat_exe = hashcat_dir / "hashcat.exe"
    if hashcat_exe.exists():
        print(f"  Installed: {hashcat_exe}")
        return hashcat_exe

    print("  Installation failed.")
    return None


def install_john_windows() -> Optional[Path]:
    """Download and install john on Windows."""
    tools_dir = get_tools_dir()
    john_dir = tools_dir / "john"

    # Check if already installed
    john_exe = john_dir / "run" / "john.exe"
    if john_exe.exists():
        print("  john already installed.")
        return john_exe

    print()
    print("Installing john the ripper for Windows...")

    # Create tools directory
    tools_dir.mkdir(parents=True, exist_ok=True)

    url = JOHN_URLS["Windows"]
    if not url:
        print("  No download URL available.")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = Path(tmpdir) / "john.zip"

        if not download_with_progress(url, archive_path, "  Downloading john"):
            return None

        # Extract
        extract_dir = Path(tmpdir) / "extract"
        extract_dir.mkdir()

        if not extract_archive(archive_path, extract_dir):
            return None

        # Find extracted folder
        extracted = list(extract_dir.iterdir())
        if not extracted:
            print("  No files extracted.")
            return None

        src_dir = extracted[0]

        # Move to tools dir
        if john_dir.exists():
            shutil.rmtree(john_dir)
        shutil.move(str(src_dir), str(john_dir))

    john_exe = john_dir / "run" / "john.exe"
    if john_exe.exists():
        print(f"  Installed: {john_exe}")
        return john_exe

    print("  Installation failed.")
    return None


def show_install_menu() -> tuple[str, dict]:
    """Show tool installation menu and return game mode + tools.

    Returns:
        Tuple of (game_mode, tools_dict)
    """
    from spellengine.cli import (
        check_cracking_tools, determine_game_mode,
        GAME_MODE_OBSERVER, GAME_MODE_HASHCAT, GAME_MODE_JOHN, GAME_MODE_FULL
    )

    # Check current tools
    tools = check_cracking_tools()

    # Also check our tools directory
    local_hashcat = get_hashcat_path()
    local_john = get_john_path()

    if local_hashcat and not tools["hashcat"]:
        tools["hashcat"] = str(local_hashcat)
    if local_john and not tools["john"]:
        tools["john"] = str(local_john)

    mode = determine_game_mode(tools)

    # If we have tools, just continue
    if mode != GAME_MODE_OBSERVER:
        return mode, tools

    # No tools - show menu
    print()
    print("=" * 60)
    print("          THE DREAD CITADEL - TOOL SETUP")
    print("=" * 60)
    print()
    print("  No cracking tools detected.")
    print()
    print("  The Dread Citadel teaches hash cracking techniques.")
    print("  For the full experience, you need hashcat or john.")
    print()
    print("  OPTIONS:")
    print()
    print("  [1] Download hashcat (Recommended)")
    print("      ~20MB - Fast GPU/CPU hash cracker")
    print()
    print("  [2] Download john the ripper")
    print("      ~15MB - Classic password cracker")
    print()
    print("  [3] Observer Mode")
    print("      No tools needed - answers revealed automatically")
    print()
    print("  [4] I have tools installed")
    print("      Re-scan or enter custom path")
    print()
    print("=" * 60)

    while True:
        try:
            choice = input("\n  Choice [1/2/3/4]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            sys.exit(0)

        if choice == "1":
            # Install hashcat
            if platform.system() == "Windows":
                hashcat_path = install_hashcat_windows()
                if hashcat_path:
                    tools["hashcat"] = str(hashcat_path)
                    print("\n  hashcat installed successfully!")
                    print("  Starting game with full cracking mode...")
                    return determine_game_mode(tools), tools
                else:
                    print("\n  Installation failed. Try Observer Mode or manual install.")
            else:
                print("\n  On macOS/Linux, install via package manager:")
                print("    macOS:  brew install hashcat")
                print("    Linux:  sudo apt install hashcat")
                print("\n  Then restart the game.")
                continue

        elif choice == "2":
            # Install john
            if platform.system() == "Windows":
                john_path = install_john_windows()
                if john_path:
                    tools["john"] = str(john_path)
                    print("\n  john installed successfully!")
                    print("  Starting game with cracking mode...")
                    return determine_game_mode(tools), tools
                else:
                    print("\n  Installation failed. Try Observer Mode or manual install.")
            else:
                print("\n  On macOS/Linux, install via package manager:")
                print("    macOS:  brew install john")
                print("    Linux:  sudo apt install john")
                print("\n  Then restart the game.")
                continue

        elif choice == "3":
            # Observer mode
            print("\n  Starting in Observer Mode...")
            print("  Press [H] during encounters to reveal answers.")
            return GAME_MODE_OBSERVER, tools

        elif choice == "4":
            # Custom path
            print("\n  Enter path to hashcat or john executable:")
            try:
                custom_path = input("  Path: ").strip()
            except (EOFError, KeyboardInterrupt):
                continue

            if custom_path:
                custom_path = Path(custom_path)
                if custom_path.exists():
                    name = custom_path.stem.lower()
                    if "hashcat" in name:
                        tools["hashcat"] = str(custom_path)
                    elif "john" in name:
                        tools["john"] = str(custom_path)
                    else:
                        print("  Could not determine tool type from filename.")
                        continue

                    new_mode = determine_game_mode(tools)
                    if new_mode != GAME_MODE_OBSERVER:
                        print(f"\n  Tool found! Starting game...")
                        return new_mode, tools
                else:
                    print(f"  File not found: {custom_path}")

            # Re-scan
            print("\n  Re-scanning for tools...")
            tools = check_cracking_tools()
            local_hashcat = get_hashcat_path()
            local_john = get_john_path()
            if local_hashcat:
                tools["hashcat"] = str(local_hashcat)
            if local_john:
                tools["john"] = str(local_john)

            mode = determine_game_mode(tools)
            if mode != GAME_MODE_OBSERVER:
                print("  Tools found!")
                return mode, tools
            print("  Still no tools found.")

        else:
            print("  Invalid choice. Enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    # Test the installer
    mode, tools = show_install_menu()
    print(f"\nMode: {mode}")
    print(f"Tools: {tools}")
