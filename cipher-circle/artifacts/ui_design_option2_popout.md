# UI Design Option 2: Pop-out Shell (Active Design)

## Window Specifications

### Story Window (Static, Non-resizable)

| Property | Value | Notes |
|----------|-------|-------|
| **Columns** | 120 | Wide enough for art + prose |
| **Rows** | 45 | Tall enough for art block + story + status |
| **Pixel Size** | ~1080 x 810 | At 9px font |
| **Monitor %** | ~56% width, 75% height | On 1920x1080 |

### Tool Window (Pops on Challenge)

| Property | Value | Notes |
|----------|-------|-------|
| **Columns** | 100 | Standard wide terminal |
| **Rows** | 30 | Enough for command history |
| **Position** | Right side or below | Non-overlapping |

---

## Layout Mockups

### Mockup A: Art Header (Recommended)

```
120 columns x 45 rows
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                      │
│    ██████╗ ██████╗ ███████╗ █████╗ ██████╗      ██████╗██╗████████╗ █████╗ ██████╗ ███████╗██╗                       │
│    ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗    ██╔════╝██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║                       │
│    ██║  ██║██████╔╝█████╗  ███████║██║  ██║    ██║     ██║   ██║   ███████║██║  ██║█████╗  ██║                       │
│    ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║  ██║    ██║     ██║   ██║   ██╔══██║██║  ██║██╔══╝  ██║                       │
│    ██████╔╝██║  ██║███████╗██║  ██║██████╔╝    ╚██████╗██║   ██║   ██║  ██║██████╔╝███████╗███████╗                  │
│    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝      ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝                  │
│                                                                                                                      │
│    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      │
│    ░░                                                                                                          ░░    │
│    ░░                              ⚔️  CHAPTER 1: THE OUTER GATES  ⚔️                                           ░░    │
│    ░░                                                                                                          ░░    │
│    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░      │
│                                                                                                                      │
│  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════    │
│                                                                                                                      │
│    The Gatekeeper blocks your path - a spectral figure bound to this final outer lock.                              │
│                                                                                                                      │
│    Its form shimmers with arcane energy as it presents the seal:                                                     │
│                                                                                                                      │
│                           ╔═══════════════════════════════════════════╗                                              │
│                           ║                                           ║                                              │
│                           ║   0d107d09f5bbe40cade3de5c71e9e9b7       ║                                              │
│                           ║                                           ║                                              │
│                           ║   TYPE: MD5  ·  LENGTH: 32 chars          ║                                              │
│                           ║                                           ║                                              │
│                           ╚═══════════════════════════════════════════╝                                              │
│                                                                                                                      │
│    The Gatekeeper speaks:                                                                                            │
│                                                                                                                      │
│    "So you've cracked the simple locks. But can you think like the lazy user                                         │
│     who wants to feel clever? This password is a PHRASE - two words merged                                           │
│     into one. What might someone type when they just want IN?"                                                       │
│                                                                                                                      │
│  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════    │
│                                                                                                                      │
│    ┌─ OBJECTIVE ───────────────────────────────────────────────────────────────────────────────────────────────┐     │
│    │  Crack the Gatekeeper's MD5 hash                                                                          │     │
│    └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                                                      │
│    [H] Hint   [T] Open Tools   [S] Skip   [Q] Quit                                                                   │
│                                                                                                                      │
│  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────  │
│   XP: 45 ◆◆◆◆◇◇◇◇◇◇                                        Chapter 1  ·  Encounter 8/8  ·  ✓ Checkpoint Available   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Mockup B: Side Art Panel

```
120 columns x 45 rows
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  THE DREAD CITADEL                                                              Chapter 1: The Outer Gates          │
│  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════    │
│                                                                                                                      │
│   ┌────────────────────────────────────┐                                                                             │
│   │            _.--._                  │   THE GATEKEEPER'S CHALLENGE                                                │
│   │         .-'      '-.               │   ══════════════════════════                                                │
│   │       .'   .-```-.  '.             │                                                                             │
│   │      /   .'       '.  \            │   The Gatekeeper blocks your path - a spectral figure                       │
│   │     ;   ;  O    O   ;  ;           │   bound to this final outer lock.                                           │
│   │     |   |     __    |  |           │                                                                             │
│   │     ;   ; \  `--'  /;  ;           │   Its form shimmers with arcane energy as it presents                       │
│   │      \   \  `----'  / /            │   the seal:                                                                 │
│   │       '.  '.______.'.'             │                                                                             │
│   │         '-._______.-'              │      ╔════════════════════════════════════════╗                             │
│   │              |||                   │      ║  0d107d09f5bbe40cade3de5c71e9e9b7      ║                             │
│   │              |||                   │      ║  TYPE: MD5  ·  32 characters           ║                             │
│   │         .----'''----.              │      ╚════════════════════════════════════════╝                             │
│   │        /  /||   ||\  \             │                                                                             │
│   │       /  / ||   || \  \            │   The Gatekeeper speaks:                                                    │
│   │      /  /  ||   ||  \  \           │                                                                             │
│   │     /__/   ||   ||   \__\          │   "So you've cracked the simple locks. But can you                          │
│   │            ||   ||                 │    think like the lazy user who wants to feel clever?                       │
│   │           [__] [__]                │                                                                             │
│   │                                    │    This password is a PHRASE - two words merged into                        │
│   │       THE GATEKEEPER               │    one. What might someone type when they just want IN?"                    │
│   └────────────────────────────────────┘                                                                             │
│                                                                                                                      │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────    │
│                                                                                                                      │
│   OBJECTIVE: Crack the Gatekeeper's MD5 hash                                                                         │
│                                                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │  > Your answer: _                                                                                            │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                                      │
│   [H] Hint   [T] Open Tools   [S] Skip   [Q] Quit                                                                    │
│                                                                                                                      │
│  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════    │
│   ◆◆◆◆◇◇◇◇◇◇  45 XP                                         Encounter 8/8   ·   ✓ Checkpoint   ·   0 Deaths        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Mockup C: Full-Width Story (Minimal Chrome)

```
120 columns x 45 rows
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                      │
│                                                                                                                      │
│                                          ▄▄▄█████▓ ██░ ██ ▓█████                                                     │
│                                          ▓  ██▒ ▓▒▓██░ ██▒▓█   ▀                                                     │
│                                          ▒ ▓██░ ▒░▒██▀▀██░▒███                                                       │
│                                          ░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄                                                     │
│                                            ▒██▒ ░ ░▓█▒░██▓░▒████▒                                                    │
│                                            ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░                                                    │
│                                 ▄████  ▄▄▄     ▄▄▄█████▓▓█████  ██ ▄█▀▓█████ ▓█████  ██▓███  ▓█████  ██▀███          │
│                                ██▒ ▀█▒▒████▄   ▓  ██▒ ▓▒▓█   ▀  ██▄█▒ ▓█   ▀ ▓█   ▀ ▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒        │
│                               ▒██░▄▄▄░▒██  ▀█▄ ▒ ▓██░ ▒░▒███   ▓███▄░ ▒███   ▒███   ▓██░ ██▓▒▒███   ▓██ ░▄█ ▒        │
│                               ░▓█  ██▓░██▄▄▄▄██░ ▓██▓ ░ ▒▓█  ▄ ▓██ █▄ ▒▓█  ▄ ▒▓█  ▄ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄          │
│                               ░▒▓███▀▒ ▓█   ▓██▒ ▒██▒ ░ ░▒████▒▒██▒ █▄░▒████▒░▒████▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒        │
│                                                                                                                      │
│                                                                                                                      │
│                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                        │
│                                                                                                                      │
│                                                                                                                      │
│         The Gatekeeper blocks your path - a spectral figure bound to this final outer lock.                         │
│                                                                                                                      │
│         Its form shimmers with arcane energy as it presents the seal:                                                │
│                                                                                                                      │
│                                                                                                                      │
│                              ┌─────────────────────────────────────────────────┐                                     │
│                              │                                                 │                                     │
│                              │       0d107d09f5bbe40cade3de5c71e9e9b7          │                                     │
│                              │                                                 │                                     │
│                              │       MD5  ·  32 characters                     │                                     │
│                              │                                                 │                                     │
│                              └─────────────────────────────────────────────────┘                                     │
│                                                                                                                      │
│                                                                                                                      │
│         "So you've cracked the simple locks. But can you think like the lazy user who                               │
│          wants to feel clever? This password is a PHRASE - two words merged into one.                               │
│                                                                                                                      │
│          What might someone type when they just want IN?"                                                            │
│                                                                                                                      │
│                                                                                                                      │
│                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                        │
│                                                                                                                      │
│         OBJECTIVE: Crack the Gatekeeper's MD5 hash                                                                   │
│                                                                                                                      │
│         > _                                                                             [H]int  [T]ools  [Q]uit      │
│                                                                                                                      │
│  ◆◆◆◆◇◇  45 XP                           The Outer Gates  ·  8/8                              ✓ Checkpoint          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Tool Window (Pops on [T])

```
100 columns x 30 rows
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  PATTERNFORGE WORKBENCH                                                        [X] Return to Story │
│  ══════════════════════════════════════════════════════════════════════════════════════════════════│
│                                                                                                    │
│  Target Hash: 0d107d09f5bbe40cade3de5c71e9e9b7                                                     │
│  Identified:  MD5 (32 characters)                                                                  │
│                                                                                                    │
│  ──────────────────────────────────────────────────────────────────────────────────────────────────│
│                                                                                                    │
│  $ pf identify 0d107d09f5bbe40cade3de5c71e9e9b7                                                    │
│  → MD5 (confidence: 98%)                                                                           │
│                                                                                                    │
│  $ pf crack 0d107d09f5bbe40cade3de5c71e9e9b7 --wordlist common                                     │
│  → Searching 10,000 common passwords...                                                            │
│  → FOUND: letmein                                                                                  │
│                                                                                                    │
│  ──────────────────────────────────────────────────────────────────────────────────────────────────│
│                                                                                                    │
│  Commands:                                                                                         │
│    pf identify <hash>              Identify hash type                                              │
│    pf crack <hash> --wordlist      Crack using wordlist                                            │
│    pf crack <hash> --mask          Crack using mask pattern                                        │
│    pf wordlist list                Show available wordlists                                        │
│    pf mask help                    Show mask notation                                              │
│    submit <answer>                 Submit answer to challenge                                      │
│    exit                            Return to story                                                 │
│                                                                                                    │
│  ──────────────────────────────────────────────────────────────────────────────────────────────────│
│                                                                                                    │
│  $ _                                                                                               │
│                                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Window Management

### macOS Implementation

```bash
# Story window - fixed size, no resize
osascript -e '
tell application "Terminal"
    set storyWindow to do script ""
    set bounds of front window to {50, 50, 1130, 860}
    -- Lock size via Terminal preferences or wrapper
end tell
'
```

### Dimensions Summary

| Window | Columns | Rows | Pixels (approx) | Position |
|--------|---------|------|-----------------|----------|
| Story | 120 | 45 | 1080 x 810 | Left/Center |
| Tools | 100 | 30 | 900 x 540 | Right/Below |

### Behavior

1. Story window opens at campaign start
2. Size is LOCKED - no resize handles
3. [T] opens Tool window alongside (non-overlapping)
4. Tool window can be closed, story persists
5. Answer submitted in either window syncs state

---

## Recommendations

**Pick: Mockup C (Full-Width Story)** because:
- Maximum immersion
- Cleanest look
- Most room for pixel art banners
- Minimal UI chrome

**Alternative: Mockup B** if we want per-encounter art that changes frequently

---

*Active design - Option 2 Pop-out Shell*
