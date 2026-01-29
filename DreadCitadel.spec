# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Dread Citadel macOS app.
"""

import sys
from pathlib import Path

block_cipher = None

# Project root
project_root = Path("/Users/petermckernan/Projects/SpellEngine")

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
    hooksconfig={},
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
    name="Dread Citadel",
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
    name="Dread Citadel",
)

app = BUNDLE(
    coll,
    name="Dread Citadel.app",
    icon=str(project_root / "assets" / "images" / "patternforge_icon.icns") if (project_root / "assets" / "images" / "patternforge_icon.icns").exists() else None,
    bundle_identifier="com.cipherCircle.dreadCitadel",
    info_plist={
        'CFBundleName': 'Dread Citadel',
        'CFBundleDisplayName': 'Dread Citadel',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.cipherCircle.dreadCitadel',
        'CFBundleExecutable': 'Dread Citadel',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'DRCT',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.games',
    },
)
