# Storysmith Tester Quick Start

```
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     You have been chosen to test the Dread Citadel.         ║
    ║                                                              ║
    ║     Few have seen these halls. Fewer still have survived.   ║
    ║                                                              ║
    ║     ...but we believe in you, Infiltrator.                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
```

Welcome to the Circle! Let's get you into the game.

---

## Prerequisites

- Python 3.10+
- Git access to this repo (you should have it if you're reading this)
- ~30 minutes for first playthrough

---

## Installation (One-Time Setup)

### Step 1: Clone Both Repos

```bash
# Clone PatternForge (the analysis engine)
git clone git@github.com:TheCipherCircle/PatternForge.git

# Clone Storysmith (the game - you're probably already here)
git clone git@github.com:TheCipherCircle/Storysmith.git
```

### Step 2: Install PatternForge

```bash
cd PatternForge
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

### Step 3: Install Storysmith

```bash
cd ../Storysmith
pip install -e .
pip install pygame           # For graphical mode
```

### Step 4: Verify Installation

```bash
# Check PatternForge
patternforge --version

# Check Storysmith
python3 -m storysmith --help
```

---

## Play the Game

### Option A: Full GUI Mode (Recommended)

```bash
python3 -m storysmith play dread_citadel
```

### Option B: Terminal Mode (Two Covers)

```bash
python3 -m storysmith play dread_citadel
```

### Option C: Text-Only Mode (Minimal)

```bash
python3 -m storysmith play dread_citadel --text
```

---

## Controls

| Key | Action |
|-----|--------|
| **Enter** | Submit answer / Continue |
| **[F]** | Launch PatternForge crack tool |
| **[H]** | Show/hide hint |
| **[B]** | Retreat (boss encounters) |
| **ESC** | Quit to title |
| **Arrow keys** | Navigate menus |

---

## If You Get Stuck

- Press **[H]** for hints
- Press **[F]** to auto-crack the hash
- Check the answer key below (spoilers!)

---

## Reporting Bugs

### Quick Report Format

```
What happened:
Steps to reproduce:
Error message (if any):
System: [macOS/Windows/Linux] Python [version]
```

### System Diagnostic

```bash
echo "=== System ===" && uname -a && python3 --version && \
cd /path/to/Storysmith && git rev-parse --short HEAD && \
cd /path/to/PatternForge && git rev-parse --short HEAD
```

### Severity Guide

| Level | When to Use |
|-------|-------------|
| **Show-stopper** | Can't start game, crash, data loss |
| **Major** | Feature broken, hard to work around |
| **Minor** | Something's off, but playable |
| **Cosmetic** | Visual/text issue only |

### Want to Fix It?

You can fix bugs with your own Claude instance:
1. Create branch: `git checkout -b fix/short-description`
2. Fix with Claude's help
3. Run tests: `pytest`
4. Push and notify pitl0rd

---

## Answer Key (SPOILERS)

<details>
<summary>Click to reveal answers</summary>

**Chapter 1: The Outer Gates**
- password, 123456, admin, letmein

**Chapter 2: The Crypts**
- 1234, John2024, dragon OR master, hello, shadow OR trustno1, secret

**Chapter 3: The Inner Sanctum**
- sunshine, Summer2024, password123

</details>

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'patternforge'"

PatternForge isn't installed. Run:
```bash
cd /path/to/PatternForge
pip install -e .
```

### "ModuleNotFoundError: No module named 'pygame'"

Pygame isn't installed. Run:
```bash
pip install pygame
```

### Game crashes on launch

Check both repos are on latest:
```bash
cd /path/to/PatternForge && git pull
cd /path/to/Storysmith && git pull
pip install -e .  # In both dirs
```

---

---

## Your Mission

Break things. Find bugs. Have fun. Every issue you find is one less bug for our users.

You're not just a tester - you're an early Infiltrator of the Dread Citadel.

**May your hashes crack swiftly.**

```
    ┌─────────────────────────────────────────┐
    │  "The Circle remembers those who help   │
    │   forge its blades."                    │
    │                                         │
    │   — The Cipher Circle                   │
    └─────────────────────────────────────────┘
```
