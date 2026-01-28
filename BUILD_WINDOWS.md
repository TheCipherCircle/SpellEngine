# Building Dread Citadel for Windows

This guide explains how to build a standalone Windows executable (.exe) that
requires **no Python installation, no pip, no git** - just double-click and play.

## Important: Cross-Compilation Not Supported

PyInstaller **cannot cross-compile** between platforms. You must build the Windows
executable on a Windows machine. The macOS build produces a macOS app bundle only.

## Quick Start (Windows)

### 1. Install Python (if not already installed)

Download Python 3.10+ from https://python.org

During installation:
- Check "Add Python to PATH"
- Check "Install pip"

### 2. Clone or Download the Repository

```powershell
git clone https://github.com/TheCipherCircle/Storysmith.git
cd Storysmith
```

Or download and extract the ZIP from GitHub.

### 3. Install Build Dependencies

```powershell
pip install pyinstaller pygame pyyaml psutil
```

### 4. Build the Executable

```powershell
python scripts\build_windows_exe.py
```

### 5. Find Your Executable

The build creates:
- `dist/DreadCitadel.exe` - The standalone executable
- `dist/DreadCitadel-Windows.zip` - Ready-to-share release package

## Manual Build (Alternative)

If the build script doesn't work, you can run PyInstaller directly:

```powershell
pyinstaller --clean --noconfirm storysmith_windows.spec
```

## What Gets Bundled

The executable includes:
- Python runtime (no Python installation needed)
- pygame library
- pyyaml library
- All game assets (images, audio)
- Campaign YAML files
- Lore content

Total size: approximately 40-60 MB

## Troubleshooting

### "pygame not found" Error

Make sure pygame is installed:
```powershell
pip install pygame
```

### Missing DLLs

If you get DLL errors when running the built exe, install the Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Antivirus False Positives

Some antivirus programs flag PyInstaller executables. This is a known issue with
all PyInstaller-built applications. You may need to whitelist the executable.

### Build Fails with "No module named..."

Ensure you're in the project root directory and the virtual environment (if any)
is activated:
```powershell
cd C:\path\to\Storysmith
python -m pip install pygame pyyaml psutil pyinstaller
python scripts\build_windows_exe.py
```

## Testing the Build

Before distributing:

1. Run `DreadCitadel.exe` on a clean Windows machine (no Python installed)
2. Verify the title screen loads with correct graphics
3. Start a new game and play through the first encounter
4. Confirm audio works (if sound files are present)
5. Test Observer Mode (the game should work even without hashcat/john)

## Distribution

The `DreadCitadel-Windows.zip` contains:
- `DreadCitadel.exe` - The game
- `README.txt` - User instructions

Share this ZIP file. Recipients just extract and double-click the exe.

## Technical Details

### Spec File

The build configuration is in `storysmith_windows.spec`. Key settings:

- `console=False` - No command prompt window
- `icon=...patternforge_icon.ico` - Custom Windows icon
- `upx=True` - Compress executable (requires UPX installed)
- `onefile=True` - Single executable (via EXE() with all data bundled)

### Resource Paths

The `storysmith/launcher.py` module handles finding bundled resources at runtime
using PyInstaller's `sys._MEIPASS` for the temp extraction directory.

### Excluded Modules

To reduce size, these are excluded:
- tkinter
- matplotlib
- numpy
- scipy
- pandas
- PIL
- tensorflow
- torch
- pytest/unittest

## Building for Other Platforms

### macOS

```bash
# On macOS, use the macOS spec file (create one if needed)
pyinstaller --onefile --windowed \
    --icon=assets/images/patternforge_icon.icns \
    --name "Dread Citadel" \
    storysmith/launcher.py
```

### Linux

```bash
# On Linux
pyinstaller --onefile \
    --name dread-citadel \
    storysmith/launcher.py
```

## CI/CD Considerations

For automated Windows builds, use GitHub Actions with `windows-latest`:

```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyinstaller pygame pyyaml psutil
      - run: python scripts/build_windows_exe.py
      - uses: actions/upload-artifact@v4
        with:
          name: DreadCitadel-Windows
          path: dist/DreadCitadel-Windows.zip
```
