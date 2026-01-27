# The Two Covers - Interactive Book UI Design

> *"A book that opens both ways - story on one cover, craft on the other"*

## Concept

Two equal-sized windows side by side, like an open book:
- **Left Cover:** Art, narrative, story, world-building
- **Right Cover:** PatternForge workflow (Wizard/Shell/CLI based on encounter)

Both windows are the same size. Always visible together. The technical depth on the right matches the narrative depth on the left.

```
┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐
│                                     │ │                                     │
│          STORY COVER                │ │          CRAFT COVER                │
│                                     │ │                                     │
│     Art · Narrative · World         │ │     Wizard · Shell · CLI            │
│                                     │ │                                     │
│     "The why and the wonder"        │ │     "The how and the doing"         │
│                                     │ │                                     │
└─────────────────────────────────────┘ └─────────────────────────────────────┘
                              THE OPEN BOOK
```

---

## Window Specifications

| Property | Story Cover | Craft Cover |
|----------|-------------|-------------|
| **Columns** | 80 | 80 |
| **Rows** | 45 | 45 |
| **Pixels** | ~720 × 810 | ~720 × 810 |
| **Combined** | 160 cols × 45 rows | ~1440 × 810 px total |
| **Position** | Left | Right |

Both windows: **Static, non-resizable, always paired**

---

## The Three Workflow Levels

### Level 1: WIZARD (Training Wheels)

For: Complete beginners, tutorial encounters, first exposure to concepts

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  PATTERNFORGE WIZARD                                              Tier 0-1  │
│  ════════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  Your target:                                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  5f4dcc3b5aa765d61d8327deb882cf99                                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Step 1: What type of hash is this?                                          │
│                                                                              │
│    [1] MD5  (32 characters) ◄── This one!                                    │
│    [2] SHA1 (40 characters)                                                  │
│    [3] I'm not sure (show me how to tell)                                    │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Step 2: How should we attack it?                                            │
│                                                                              │
│    [1] Try common passwords (wordlist)                                       │
│    [2] Try patterns like Name1234 (mask)                                     │
│    [3] Explain the difference                                                │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Step 3: Enter your guess                                                    │
│                                                                              │
│    > _                                                                       │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│  [?] Why these steps?   [↑] Back   [Enter] Submit                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Step-by-step guidance
- Multiple choice where possible
- "Explain" options at each step
- No command memorization required
- Errors are impossible (guided paths only)

---

### Level 2: SHELL (Interactive Exploration)

For: Intermediate encounters, after tutorial, building confidence

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  PATTERNFORGE SHELL                                               Tier 2-3  │
│  ════════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  Target: 0d107d09f5bbe40cade3de5c71e9e9b7 (MD5)                              │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  pf> identify                                                                │
│  → MD5 (32 characters, confidence: 98%)                                      │
│                                                                              │
│  pf> wordlist list                                                           │
│  → common     (10,000 passwords)                                             │
│  → rockyou    (14 million passwords)                                         │
│  → names      (50,000 first names)                                           │
│                                                                              │
│  pf> crack --wordlist common                                                 │
│  → Trying 10,000 passwords...                                                │
│  → FOUND: letmein                                                            │
│                                                                              │
│  pf> submit letmein                                                          │
│  → ✓ Correct! Returning to story...                                          │
│                                                                              │
│  pf> _                                                                       │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Commands: identify, crack, wordlist, mask, submit, help, hint               │
│  Tab completion enabled · ↑↓ for history                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Interactive REPL-style interface
- Tab completion for commands
- Simplified command set (not full CLI)
- Context-aware (target hash pre-loaded)
- `help` shows available commands
- Errors give helpful suggestions

---

### Level 3: CLI (Full Power)

For: Advanced encounters, boss fights, post-game challenges

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  PATTERNFORGE CLI                                                 Tier 4-6  │
│  ════════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  $ patternforge identify cbfdac6008f9cab4083784cbd1874f76618d2a97            │
│  SHA1 (40 characters)                                                        │
│  Possible modes: 100, 300, 6000                                              │
│                                                                              │
│  $ patternforge crack \                                                      │
│      --hash cbfdac6008f9cab4083784cbd1874f76618d2a97 \                       │
│      --type sha1 \                                                           │
│      --attack hybrid \                                                       │
│      --wordlist common \                                                     │
│      --mask '?d?d?d'                                                         │
│                                                                              │
│  [*] Hybrid attack: common.txt + ?d?d?d                                      │
│  [*] Keyspace: 10,000,000 candidates                                         │
│  [*] Speed: 2.4 MH/s                                                         │
│  [*] ETA: 4 seconds                                                          │
│                                                                              │
│  cbfdac6008f9cab4083784cbd1874f76618d2a97:password123                        │
│                                                                              │
│  Session complete. 1 hash recovered.                                         │
│                                                                              │
│  $ submit password123                                                        │
│  ✓ The Citadel Lord falls!                                                   │
│                                                                              │
│  $ _                                                                         │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────  │
│  Full CLI · man patternforge for help · No guardrails                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- Full PatternForge CLI
- Real command syntax (transferable skill!)
- No hand-holding
- Complex flags and options available
- Pipe support, scripting possible
- Matches actual tool usage

---

## Encounter Workflow Tagging

Each encounter in campaign YAML specifies its workflow level:

```yaml
encounters:
  - id: enc_first_lock
    title: "The First Lock"
    type: flash
    tier: 0
    workflow: wizard          # ← Workflow level
    xp_reward: 15

  - id: enc_gatekeeper
    title: "The Gatekeeper's Challenge"
    type: flash
    tier: 1
    workflow: shell           # ← Workflow level
    xp_reward: 20

  - id: enc_citadel_lord
    title: "The Citadel Lord"
    type: flash
    tier: 3
    workflow: cli             # ← Workflow level (boss fight!)
    xp_reward: 35
```

### Workflow Field Values

| Value | Level | Tier Range | Use Case |
|-------|-------|------------|----------|
| `wizard` | 1 | 0-1 | Tutorial, first exposure |
| `shell` | 2 | 2-3 | Building confidence |
| `cli` | 3 | 4-6 | Advanced, boss fights |
| `choice` | Any | Any | Player picks their level |

---

## The Two Covers - Full Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                              │                                                                                  │
│                     ██████╗  ██████╗ ███████╗ █████╗ ██████╗                 │   PATTERNFORGE WIZARD                                              Tier 0       │
│                     ██╔══██╗ ██╔══██╗██╔════╝██╔══██╗██╔══██╗                │   ═══════════════════════════════════════════════════════════════════════════   │
│                     ██║  ██║ ██████╔╝█████╗  ███████║██║  ██║                │                                                                                  │
│                     ██║  ██║ ██╔══██╗██╔══╝  ██╔══██║██║  ██║                │   Your target:                                                                   │
│                     ██████╔╝ ██║  ██║███████╗██║  ██║██████╔╝                │   ┌──────────────────────────────────────────────────────────────────────────┐   │
│                     ╚═════╝  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝                 │   │  5f4dcc3b5aa765d61d8327deb882cf99                                        │   │
│                                                                              │   └──────────────────────────────────────────────────────────────────────────┘   │
│                            CHAPTER 1: THE OUTER GATES                        │                                                                                  │
│                                                                              │   Step 1: What type of hash is this?                                            │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │                                                                                  │
│                                                                              │     [1] MD5  (32 characters) ◄                                                  │
│                                                                              │     [2] SHA1 (40 characters)                                                    │
│                         ┌─────────────────────────┐                          │     [3] I'm not sure                                                            │
│                         │                         │                          │                                                                                  │
│                         │      THE FIRST LOCK     │                          │   ─────────────────────────────────────────────────────────────────────────────  │
│                         │                         │                          │                                                                                  │
│                         │    ╔═══════════════╗    │                          │   Step 2: How should we attack it?                                              │
│                         │    ║   ░░░███░░░   ║    │                          │                                                                                  │
│                         │    ║   ░░█████░░   ║    │                          │     [1] Try common passwords (wordlist)                                         │
│                         │    ║   █████████   ║    │                          │     [2] Try patterns (mask)                                                     │
│                         │    ║   ░░█████░░   ║    │                          │                                                                                  │
│                         │    ║   ░░░███░░░   ║    │                          │   ─────────────────────────────────────────────────────────────────────────────  │
│                         │    ╚═══════════════╝    │                          │                                                                                  │
│                         │                         │                          │   Step 3: Enter your guess                                                       │
│                         └─────────────────────────┘                          │                                                                                  │
│                                                                              │     > _                                                                          │
│   Before you stands the first gate, sealed with a simple lock.               │                                                                                  │
│   Etched into its surface is an MD5 hash:                                    │                                                                                  │
│                                                                              │                                                                                  │
│       5f4dcc3b5aa765d61d8327deb882cf99                                       │                                                                                  │
│                                                                              │                                                                                  │
│   The Cipher Circle whispers: "This password is so common, so                │                                                                                  │
│   obvious, that it might be the very word you're thinking of                 │   ─────────────────────────────────────────────────────────────────────────────  │
│   right now..."                                                              │   [?] Why these steps?   [↑] Back   [Enter] Submit                              │
│                                                                              │                                                                                  │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │                                                                                  │
│                                                                              │                                                                                  │
│   OBJECTIVE: Crack the hash - what password produces this MD5?               │                                                                                  │
│                                                                              │                                                                                  │
│   ◆◇◇◇◇◇  15 XP                            Encounter 3/8                     │                                                                                  │
│                                                                              │                                                                                  │
└──────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────┘
          STORY COVER                                                                    CRAFT COVER (WIZARD MODE)
```

---

## Workflow Progression Through Dread Citadel

| Encounter | Current Workflow | Proposed |
|-----------|------------------|----------|
| enc_the_approach | N/A (tour) | - |
| enc_what_guards | N/A (tour) | - |
| **enc_first_lock** | manual | `wizard` |
| enc_wordsmith_wisdom | N/A (tour) | - |
| **enc_common_tongue** | manual | `wizard` |
| **enc_servants_key** | manual | `wizard` |
| enc_inner_threshold | N/A (checkpoint) | - |
| **enc_gatekeeper** | manual | `shell` |
| enc_descending | N/A (tour) | - |
| enc_pattern_weaver | N/A (tour) | - |
| **enc_simple_patterns** | manual | `shell` |
| **enc_name_game** | manual | `shell` |
| enc_crossroads | N/A (fork) | - |
| **enc_ancient_scroll** | manual | `shell` |
| **enc_pattern_lock** | manual | `shell` |
| enc_different_cipher | N/A (tour) | - |
| **enc_sha1_first_test** | manual | `shell` |
| enc_trapped_chest | N/A (gambit) | - |
| **enc_safe_crack** | manual | `shell` |
| **enc_risky_crack** | manual | `shell` |
| enc_deep_archive | N/A (checkpoint) | - |
| **enc_crypt_guardian** | manual | `shell` |
| enc_final_ascent | N/A (tour) | - |
| **enc_left_hand** | manual | `cli` |
| **enc_right_hand** | manual | `cli` |
| enc_lords_chamber | N/A (fork) | - |
| **enc_citadel_lord** | manual | `cli` |
| enc_victory | N/A (tour) | - |
| enc_beyond | N/A (tour) | - |

**Summary:**
- **WIZARD:** 3 encounters (Chapter 1 intro)
- **SHELL:** 9 encounters (Chapter 2 meat)
- **CLI:** 3 encounters (Chapter 3 finale)
- **N/A:** 13 encounters (tours, forks, checkpoints)

---

## Implementation Notes

### Window Management

```python
# Open both covers together
def open_two_covers():
    # Story cover - left side
    story_window = open_terminal(
        cols=80, rows=45,
        position="left",
        resizable=False
    )

    # Craft cover - right side
    craft_window = open_terminal(
        cols=80, rows=45,
        position="right",
        resizable=False
    )

    return story_window, craft_window
```

### Workflow Switching

```python
def load_encounter_workflow(encounter):
    """Load appropriate workflow based on encounter config."""

    if encounter.workflow == "wizard":
        return WizardWorkflow(encounter)
    elif encounter.workflow == "shell":
        return ShellWorkflow(encounter)
    elif encounter.workflow == "cli":
        return CLIWorkflow(encounter)
    elif encounter.workflow == "choice":
        return prompt_workflow_choice()
    else:
        return None  # Tour/fork/checkpoint - no craft cover
```

### Answer Sync

Both covers can accept answers:
- Story cover: Simple `> answer` prompt
- Craft cover: `submit <answer>` command

Both sync to same game state.

---

## Visual Balance Principles

1. **Equal weight:** Both covers same size, same visual density
2. **Complementary content:** Story explains *why*, Craft shows *how*
3. **Progressive complexity:** Wizard → Shell → CLI mirrors narrative stakes
4. **Breathing room:** Generous margins, not cramped
5. **Consistent chrome:** Same border styles, same status bar format

---

## The Book Metaphor

```
     ┌─────────────────┐
    ╱                   ╲
   ╱  "Every hash has   ╲
  ╱    a story to tell.  ╲
 ╱                        ╲
╱  One cover shows the     ╲
│  tale - the mystery,     │
│  the challenge, the      │
│  world you're in.        │
│                          │
│  The other cover shows   │
│  the craft - the tools,  │
│  the technique, the      │
│  skill you're building." │
╲                          ╱
 ╲                        ╱
  ╲  Open both covers.   ╱
   ╲  Read the story.   ╱
    ╲  Do the work.    ╱
     ╲________________╱

      THE TWO COVERS
```

---

*Active design document - Two Covers UI system*
