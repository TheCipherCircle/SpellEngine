# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Storysmith / Dread Citadel

Builds a single-file Windows executable that launches the game directly.
No terminal, no pip, no git required - just double-click and play.

Build on Windows with:
    pyinstaller storysmith_windows.spec

Or use the build script:
    python scripts/build_windows_exe.py
"""

import sys
from pathlib import Path

# Get the project root directory
SPEC_ROOT = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_ROOT

# Data files to bundle
datas = [
    # Campaign YAML files
    (str(PROJECT_ROOT / 'content'), 'content'),
    # Image assets
    (str(PROJECT_ROOT / 'assets' / 'images'), 'assets/images'),
    # Audio assets
    (str(PROJECT_ROOT / 'assets' / 'audio'), 'assets/audio'),
    # Lore files (if needed by game)
    (str(PROJECT_ROOT / 'lore'), 'lore'),
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
    'pygame.transform',
    'pygame.surface',
    'yaml',
    'pyyaml',
    'psutil',  # Used by agents/math_validator.py
    'pydantic',  # Used by adventures/models.py
    'pydantic.fields',
    'pydantic.main',
    'pydantic_core',
    # All storysmith modules
    'storysmith',
    'storysmith.cli',
    'storysmith.adventures',
    'storysmith.adventures.loader',
    'storysmith.adventures.models',
    'storysmith.adventures.state',
    'storysmith.adventures.assets',
    'storysmith.adventures.achievements',
    'storysmith.adventures.ascii_art',
    'storysmith.adventures.dice',
    'storysmith.adventures.experience_grading',
    'storysmith.adventures.hashlib_designed',
    'storysmith.adventures.validation',
    'storysmith.engine',
    'storysmith.engine.game',
    'storysmith.engine.game.client',
    'storysmith.engine.game.audio',
    'storysmith.engine.game.renderer',
    'storysmith.engine.game.scenes',
    'storysmith.engine.game.scenes.base',
    'storysmith.engine.game.scenes.title',
    'storysmith.engine.game.scenes.encounter',
    'storysmith.engine.game.scenes.game_over',
    'storysmith.engine.game.scenes.victory',
    'storysmith.engine.game.ui',
    'storysmith.engine.game.ui.theme',
    'storysmith.engine.game.ui.button',
    'storysmith.engine.game.ui.panel',
    'storysmith.engine.game.ui.text',
    'storysmith.engine.game.ui.textbox',
    'storysmith.engine.game.ui.menu',
    'storysmith.engine.game.ui.hash_display',
    'storysmith.content',
    'storysmith.content.indexer',
    'storysmith.agents',
    'storysmith.agents.math_validator',
    'storysmith.agents.cosmic',
    'storysmith.agents.scribe',
    'storysmith.agents.mirth',
    'storysmith.launcher',
]

# Exclude modules we don't need (reduce size)
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
    'tensorflow',
    'torch',
    'unittest',
    'test',
    'tests',
    'pytest',
    'patternforge',  # Listed as dependency but not used
]

a = Analysis(
    [str(PROJECT_ROOT / 'storysmith' / 'launcher.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DreadCitadel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No terminal window - pure GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / 'assets' / 'images' / 'patternforge_icon.ico'),
)
