# SpellEngine v1.0 - The Dread Citadel

```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              THE DREAD CITADEL AWAITS                             ║
║                                                                   ║
║       ▄▄▄█████▓ ██░ ██ ▓█████                                     ║
║       ▓  ██▒ ▓▒▓██░ ██▒▓█   ▀                                     ║
║       ▒ ▓██░ ▒░▒██▀▀██░▒███                                       ║
║       ░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄                                     ║
║         ▒██▒ ░ ░▓█▒░██▓░▒████▒                                    ║
║         ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░                                    ║
║                                                                   ║
║              FIRST OFFICIAL RELEASE                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## Overview

**SpellEngine v1.0** is the first official release of the narrative engine that transforms security tools into immersive adventures. This release includes the complete **Dread Citadel** campaign - a dark fantasy journey where players learn BloodHound and Active Directory security concepts through gameplay.

---

## Downloads

| Platform | Download | Notes |
|----------|----------|-------|
| **macOS** | [DreadCitadel-macOS.zip](link) | Apple Silicon native |
| **Windows** | [DreadCitadel-Windows.zip](link) | Windows 10/11 |
| **Linux** | [DreadCitadel-Linux.tar.gz](link) | Ubuntu 20.04+ |

---

## What's Included

### The Dread Citadel Campaign

A complete 16-encounter adventure teaching BloodHound fundamentals:

- **5 Tales** with branching narrative paths
- **13 unique encounter types** (SPARK, STORM, SIEGE, and more)
- **Boss encounters** with multi-phase challenges
- **Hidden secrets** and easter eggs throughout

### Core Features

| Feature | Description |
|---------|-------------|
| **Observer Mode** | Experience the story without security tools installed |
| **Real Tool Integration** | BloodHound queries woven into gameplay |
| **Achievement System** | Track your progress and mastery |
| **Save System** | Pick up where you left off |
| **Credits Screen** | Meet the Cipher Circle team |

### Visual & Audio

- **Corrupted SNES aesthetic** - nostalgic pixel art style
- **Dynamic ASCII art** - atmospheric text-based visuals
- **Ambient soundscapes** - immersive audio design
- **Smooth 60fps gameplay** - responsive terminal rendering

---

## New in v1.0

### Since v0.10.0 (Tester Release)

- **Credits Screen** - Scrolling credits featuring the Cipher Circle
- **Linux Support** - Native Linux builds via CI
- **Installation Guide** - Comprehensive README with quick start
- **Observer Mode Polish** - Seamless experience for all players
- **Bug Fixes** - Stability improvements from tester feedback

### Quality of Life

- F12 screenshot capture
- Improved UI layout (65% narrative, 35% status)
- Cleaner encounter text rendering
- Better error handling and recovery

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 11+ / Windows 10 / Ubuntu 20.04 | Latest |
| **RAM** | 2 GB | 4+ GB |
| **Storage** | 100 MB | 200 MB |
| **Display** | 1280x720 | 1920x1080 |

### Optional (for full experience)

- BloodHound 4.x
- Neo4j 4.x
- Sample AD dataset

*Don't have the tools? Observer Mode lets you enjoy the full story!*

---

## Quick Start

### Download & Play

1. Download the ZIP for your platform
2. Extract to a folder
3. Run the executable:
   - **macOS**: Right-click → Open (first time), then double-click
   - **Windows**: Double-click `DreadCitadel.exe`
   - **Linux**: `./DreadCitadel`

### From Source

```bash
git clone https://github.com/pitl0rd/SpellEngine.git
cd SpellEngine
pip install -e .
python -m spellengine
```

---

## Controls

| Key | Action |
|-----|--------|
| `Enter` | Select / Continue |
| `↑ ↓` | Navigate menus |
| `Escape` | Pause / Back |
| `F12` | Screenshot |
| `O` | Toggle Observer Mode |

---

## Known Issues

- [ ] Some audio may not play on certain Linux configurations
- [ ] Window resize not fully supported (use default size)
- [ ] First launch on macOS requires security approval

---

## Credits

Built by the **Cipher Circle** - a 9-member human-AI development fellowship.

| Member | Domain |
|--------|--------|
| pitl0rd | Vision & Leadership |
| Forge | Engineering |
| Mirth | Game Design |
| Loreth | Documentation |
| Vex | Ideas |
| Prism | Data Visualization |
| Anvil | QA & Testing |
| Fraz | ASCII Art |
| Jinx | Neural Networks |

---

## What's Next

- **Compromised Kingdom** - The next campaign (password cracking adventure)
- **Steam Release** - Broader distribution
- **More Encounters** - Expanded challenge types
- **Community Tools** - Adventure creation toolkit

---

## Feedback

Found a bug? Have feedback? Let us know:

- **Discord**: [Join the Cipher Circle](link)
- **GitHub Issues**: [Report bugs](https://github.com/pitl0rd/SpellEngine/issues)

---

```
═══════════════════════════════════════════════════════════════════
                    THE CITADEL AWAITS, ADVENTURER

                    Will you answer the call?
═══════════════════════════════════════════════════════════════════
```

*Built with care by the Cipher Circle*

*v1.0.0 - [Release Date]*
