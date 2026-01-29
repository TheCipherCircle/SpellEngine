# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for SpellEngine / Dread Citadel - Linux

Builds a single-file Linux executable that launches the game directly.
No terminal dependencies required - just run the binary.

Build on Linux with:
    pyinstaller spellengine_linux.spec

Or use the build script:
    python scripts/build_linux_exe.py
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
    'rich',  # Used by dice.py and CLI
    'rich.console',
    'rich.table',
    'rich.panel',
    'rich.text',
    'rich.style',
    'rich.markup',
    # All spellengine modules
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
    'spellengine.adventures.experience_grading',
    'spellengine.adventures.hashlib_designed',
    'spellengine.adventures.validation',
    'spellengine.engine',
    'spellengine.engine.game',
    'spellengine.engine.game.client',
    'spellengine.engine.game.audio',
    'spellengine.engine.game.renderer',
    'spellengine.engine.game.scenes',
    'spellengine.engine.game.scenes.base',
    'spellengine.engine.game.scenes.title',
    'spellengine.engine.game.scenes.encounter',
    'spellengine.engine.game.scenes.game_over',
    'spellengine.engine.game.scenes.victory',
    'spellengine.engine.game.ui',
    'spellengine.engine.game.ui.theme',
    'spellengine.engine.game.ui.button',
    'spellengine.engine.game.ui.panel',
    'spellengine.engine.game.ui.text',
    'spellengine.engine.game.ui.textbox',
    'spellengine.engine.game.ui.menu',
    'spellengine.engine.game.ui.hash_display',
    'spellengine.content',
    'spellengine.content.indexer',
    'spellengine.agents',
    'spellengine.agents.math_validator',
    'spellengine.agents.cosmic',
    'spellengine.agents.scribe',
    'spellengine.agents.mirth',
    'spellengine.launcher',
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
    [str(PROJECT_ROOT / 'spellengine' / 'launcher.py')],
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
)
