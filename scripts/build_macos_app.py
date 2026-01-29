#!/usr/bin/env python3
"""
Build macOS .app bundle for SpellEngine/Dread Citadel.

Creates a double-click installer that requires NO terminal, NO pip, NO git.
VIP business lead (Regent) - zero friction is critical.

Usage:
    python scripts/build_macos_app.py

Output:
    dist/Dread Citadel.app - The macOS application bundle
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# App configuration
APP_NAME = "Dread Citadel"
APP_BUNDLE_ID = "com.cipherCircle.dreadCitadel"
APP_VERSION = "1.0.0"

# PyInstaller path (user install location)
PYINSTALLER = Path.home() / "Library" / "Python" / "3.12" / "bin" / "pyinstaller"


def find_pyinstaller():
    """Find PyInstaller executable."""
    # Check user install location first
    if PYINSTALLER.exists():
        return str(PYINSTALLER)

    # Check if it's on PATH
    result = shutil.which("pyinstaller")
    if result:
        return result

    # Try python -m PyInstaller
    return [sys.executable, "-m", "PyInstaller"]


def create_launcher_script():
    """Create the main launcher script for the app."""
    launcher_path = PROJECT_ROOT / "scripts" / "app_launcher.py"

    launcher_code = '''\
#!/usr/bin/env python3
"""
Launcher script for Dread Citadel macOS app.
Automatically finds and launches the game without any user setup.
"""

import os
import sys
from pathlib import Path

def get_app_root():
    """Get the root directory of the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled app
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.parent


def setup_environment():
    """Set up the environment for running the game."""
    app_root = get_app_root()

    # Add the app root to sys.path so imports work
    sys.path.insert(0, str(app_root))

    # Set environment variables for pygame
    os.environ.setdefault('SDL_VIDEO_WINDOW_POS', '0,25')

    return app_root


def main():
    """Main entry point - launch Dread Citadel directly."""
    app_root = setup_environment()

    # Import and run the game
    from spellengine.cli import (
        play_gui_mode,
        get_campaigns,
        check_cracking_tools,
        determine_game_mode,
        GAME_MODE_OBSERVER,
    )
    from spellengine.adventures.loader import load_campaign
    from spellengine.engine.game.client import launch_game

    # Find Dread Citadel campaign
    campaigns = get_campaigns()
    campaign = next((c for c in campaigns if c["id"] == "dread_citadel"), None)

    if not campaign:
        # Fallback: look in the bundled content directory
        content_dir = app_root / "content" / "adventures" / "dread_citadel"
        campaign_file = content_dir / "campaign.yaml"

        if not campaign_file.exists():
            print("ERROR: Dread Citadel campaign not found!")
            print(f"Looked in: {content_dir}")
            sys.exit(1)

        campaign = {
            "id": "dread_citadel",
            "title": "The Dread Citadel",
            "path": content_dir,
        }

    # Check for cracking tools
    tools = check_cracking_tools()
    game_mode = determine_game_mode(tools)

    # For the app version, default to observer mode if no tools found
    # This ensures the VIP can play without installing hashcat
    if game_mode == GAME_MODE_OBSERVER:
        print("="*60)
        print("         DREAD CITADEL - OBSERVER MODE")
        print("="*60)
        print()
        print("No cracking tools (hashcat/john) detected.")
        print("Running in Observer Mode - hints will reveal answers.")
        print()
        print("For the full experience, install hashcat:")
        print("  brew install hashcat")
        print()

    # Load and launch
    try:
        campaign_file = campaign["path"] / "campaign.yaml"
        loaded_campaign = load_campaign(campaign_file)

        launch_game(
            campaign=loaded_campaign,
            player_name="Apprentice",
            resume=False,
            game_mode=game_mode,
            tools=tools,
        )
    except Exception as e:
        print(f"ERROR: Failed to launch game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

    with open(launcher_path, 'w') as f:
        f.write(launcher_code)

    os.chmod(launcher_path, 0o755)
    return launcher_path


def create_spec_file():
    """Create PyInstaller spec file for the app."""
    spec_path = PROJECT_ROOT / "DreadCitadel.spec"

    icon_path = PROJECT_ROOT / "assets" / "images" / "patternforge_icon.icns"

    spec_content = f'''\
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Dread Citadel macOS app.
"""

import sys
from pathlib import Path

block_cipher = None

# Project root
project_root = Path("{PROJECT_ROOT}")

# Data files to include
datas = [
    # Game content
    (str(project_root / "content"), "content"),
    # Asset files (images and audio)
    (str(project_root / "assets"), "assets"),
    # Lore files (if any)
    (str(project_root / "lore"), "lore"),
    # The spellengine package itself (for campaigns folder)
    (str(project_root / "spellengine" / "campaigns"), "spellengine/campaigns") if (project_root / "spellengine" / "campaigns").exists() else (str(project_root / "content"), "spellengine/campaigns"),
]

# Filter out non-existent paths
datas = [(src, dst) for src, dst in datas if Path(src).exists()]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'pygame',
    'pygame.mixer',
    'pygame.font',
    'pygame.image',
    'pygame.display',
    'pygame.event',
    'pygame.time',
    'pygame.draw',
    'pygame.surface',
    'pygame.rect',
    'pygame.color',
    'yaml',
    'pyyaml',
    'spellengine',
    'spellengine.cli',
    'spellengine.adventures',
    'spellengine.adventures.loader',
    'spellengine.adventures.models',
    'spellengine.adventures.state',
    'spellengine.adventures.assets',
    'spellengine.adventures.achievements',
    'spellengine.adventures.ascii_art',
    'spellengine.adventures.dice',
    'spellengine.adventures.validation',
    'spellengine.engine',
    'spellengine.engine.game',
    'spellengine.engine.game.client',
    'spellengine.engine.game.audio',
    'spellengine.engine.game.renderer',
    'spellengine.engine.game.ui',
    'spellengine.engine.game.ui.button',
    'spellengine.engine.game.ui.menu',
    'spellengine.engine.game.ui.panel',
    'spellengine.engine.game.ui.text',
    'spellengine.engine.game.ui.textbox',
    'spellengine.engine.game.ui.theme',
    'spellengine.engine.game.ui.hash_display',
    'spellengine.engine.game.scenes',
    'spellengine.engine.game.scenes.base',
    'spellengine.engine.game.scenes.title',
    'spellengine.engine.game.scenes.encounter',
    'spellengine.engine.game.scenes.game_over',
    'spellengine.engine.game.scenes.victory',
]

a = Analysis(
    [str(project_root / "scripts" / "app_launcher.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="{APP_NAME}",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS app behavior
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "images" / "patternforge_icon.icns") if (project_root / "assets" / "images" / "patternforge_icon.icns").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="{APP_NAME}",
)

app = BUNDLE(
    coll,
    name="{APP_NAME}.app",
    icon=str(project_root / "assets" / "images" / "patternforge_icon.icns") if (project_root / "assets" / "images" / "patternforge_icon.icns").exists() else None,
    bundle_identifier="{APP_BUNDLE_ID}",
    info_plist={{
        'CFBundleName': '{APP_NAME}',
        'CFBundleDisplayName': '{APP_NAME}',
        'CFBundleVersion': '{APP_VERSION}',
        'CFBundleShortVersionString': '{APP_VERSION}',
        'CFBundleIdentifier': '{APP_BUNDLE_ID}',
        'CFBundleExecutable': '{APP_NAME}',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'DRCT',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.games',
    }},
)
'''

    with open(spec_path, 'w') as f:
        f.write(spec_content)

    return spec_path


def build_app():
    """Build the macOS app bundle."""
    print("="*60)
    print("  Building Dread Citadel macOS App")
    print("="*60)
    print()

    # Step 1: Create launcher script
    print("Step 1: Creating launcher script...")
    launcher_path = create_launcher_script()
    print(f"  Created: {launcher_path}")

    # Step 2: Create spec file
    print("\nStep 2: Creating PyInstaller spec file...")
    spec_path = create_spec_file()
    print(f"  Created: {spec_path}")

    # Step 3: Clean previous builds
    print("\nStep 3: Cleaning previous builds...")
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if app_path.exists():
        shutil.rmtree(app_path)
        print(f"  Removed: {app_path}")

    build_path = BUILD_DIR / APP_NAME
    if build_path.exists():
        shutil.rmtree(build_path)
        print(f"  Removed: {build_path}")

    # Step 4: Install dependencies in the project
    print("\nStep 4: Installing dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(PROJECT_ROOT), "--quiet"],
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pygame", "pyyaml", "--quiet"],
        check=True,
    )
    print("  Dependencies installed")

    # Step 5: Run PyInstaller
    print("\nStep 5: Running PyInstaller...")
    pyinstaller = find_pyinstaller()

    if isinstance(pyinstaller, list):
        cmd = pyinstaller + [
            "--clean",
            "--noconfirm",
            str(spec_path),
        ]
    else:
        cmd = [
            pyinstaller,
            "--clean",
            "--noconfirm",
            str(spec_path),
        ]

    print(f"  Command: {' '.join(str(c) for c in cmd)}")
    print()

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("\nERROR: PyInstaller build failed!")
        sys.exit(1)

    # Step 6: Verify the app was created
    print("\nStep 6: Verifying build...")
    app_path = DIST_DIR / f"{APP_NAME}.app"

    if not app_path.exists():
        # Check alternate location
        alt_path = DIST_DIR / APP_NAME / f"{APP_NAME}.app"
        if alt_path.exists():
            # Move to correct location
            shutil.move(str(alt_path), str(app_path))
            print(f"  Moved app to: {app_path}")
        else:
            print(f"ERROR: App not found at {app_path} or {alt_path}")
            sys.exit(1)

    # Get app size
    app_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
    app_size_mb = app_size / (1024 * 1024)

    print(f"\n{'='*60}")
    print(f"  BUILD SUCCESSFUL!")
    print(f"{'='*60}")
    print()
    print(f"  App: {app_path}")
    print(f"  Size: {app_size_mb:.1f} MB")
    print()
    print("  To run:")
    print(f"    open \"{app_path}\"")
    print()
    print("  Or double-click in Finder!")
    print()

    return app_path


def main():
    """Main entry point."""
    try:
        build_app()
    except KeyboardInterrupt:
        print("\nBuild cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
