# Sprint 2.1 Report: Adventure State Machine

**Project:** PTHAdventures
**Sprint:** 2.1
**Date:** 2026-01-24
**Team:** The Cipher Circle

---

## Executive Summary

Sprint 2.1 established the foundation for PTHAdventures - a choose-your-own-adventure system for password cracking education. The sprint delivered a complete state machine for tracking player progress through branching narratives, with full test coverage implementing Mirth's QA test plan.

### Key Metrics

| Metric | Value |
|--------|-------|
| Tests Added | 29 |
| Total Tests | 638 |
| Files Created | 5 |
| Lines of Code | ~800 |
| Test Coverage | 100% (adventure module) |

---

## 1. Adventure Mode Design

### 1.1 Core Concept

PTHAdventures transforms password cracking education into an interactive narrative experience. Players progress through encounters that teach security concepts while making choices that affect their journey.

```
+-------------------------------------------------------------------+
|                     ADVENTURE MODE CONCEPT                         |
+-------------------------------------------------------------------+
|                                                                   |
|   PLAYER                                                          |
|     |                                                             |
|     v                                                             |
|   +------------------+                                            |
|   |    CAMPAIGN      |  "The Dread Citadel"                      |
|   +--------+---------+                                            |
|            |                                                      |
|            v                                                      |
|   +------------------+     +------------------+                   |
|   |    CHAPTER 1     | --> |    CHAPTER 2     | --> ...          |
|   | "The Gates"      |     | "The Bcrypts"    |                  |
|   +--------+---------+     +------------------+                   |
|            |                                                      |
|            v                                                      |
|   +------------------+                                            |
|   |   ENCOUNTER 1    |  FLASH: Quick hash crack                  |
|   +--------+---------+                                            |
|            |                                                      |
|            v                                                      |
|   +------------------+                                            |
|   |   ENCOUNTER 2    |  FORK: Choose your path                   |
|   +--------+---------+                                            |
|           / \                                                     |
|          /   \                                                    |
|         v     v                                                   |
|   [SUCCESS] [FAILURE]                                             |
|       |         |                                                 |
|       v         v                                                 |
|   Continue   Game Over                                            |
|              Screen                                               |
|                                                                   |
+-------------------------------------------------------------------+
```

### 1.2 Encounter Skeleton Types

The system supports 15 skeleton types organized into 5 categories:

```
+-------------------------------------------------------------------+
|                    ENCOUNTER SKELETON TYPES                        |
+-------------------------------------------------------------------+
|                                                                   |
|  INSTANT (<30 sec)          GUIDED (follow along)                 |
|  +------------------+       +------------------+                  |
|  | FLASH            |       | TOUR             |                  |
|  | Single command   |       | No-fail walkthru |                  |
|  +------------------+       +------------------+                  |
|  | LOOKUP           |       | WALKTHROUGH      |                  |
|  | Find the answer  |       | Checkpoints      |                  |
|  +------------------+       +------------------+                  |
|                                                                   |
|  OPEN (exploration)         TIMED (pressure)                      |
|  +------------------+       +------------------+                  |
|  | HUNT             |       | RACE             |                  |
|  | Search output    |       | Beat the clock   |                  |
|  +------------------+       +------------------+                  |
|  | CRAFT            |       | SIEGE            |                  |
|  | Build something  |       | Wave defense     |                  |
|  +------------------+       +------------------+                  |
|                                                                   |
|  BRANCHING (choices)        ADVANCED                              |
|  +------------------+       +------------------+                  |
|  | FORK             |       | PUZZLE_BOX       |                  |
|  | Choose path      |       | Multi-step       |                  |
|  +------------------+       +------------------+                  |
|  | GAMBIT           |       | DUEL / REPAIR    |                  |
|  | Risk/reward      |       | PIPELINE / SCRIPT|                  |
|  +------------------+       +------------------+                  |
|                                                                   |
+-------------------------------------------------------------------+
```

### 1.3 Difficulty Tiers

```
+-------------------------------------------------------------------+
|                      DIFFICULTY TIERS                              |
+-------------------------------------------------------------------+
|                                                                   |
|  Tier 0: Tutorial      |████                    | <1 sec crack   |
|  Tier 1: Trivial       |████████                | <5 sec crack   |
|  Tier 2: Easy          |████████████            | <15 sec crack  |
|  Tier 3: Normal        |████████████████        | <30 sec crack  |
|  Tier 4: Hard          |████████████████████    | <2 min crack   |
|  Tier 5: Expert        |████████████████████████| Progressive    |
|  Tier 6: Master        |████████████████████████| Multi-stage    |
|                                                                   |
|  DESIGN PRINCIPLE: Tiers 0-2 must crack INSTANTLY for teaching   |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 2. System Architecture

### 2.1 Module Structure

```
+-------------------------------------------------------------------+
|                    MODULE ARCHITECTURE                             |
+-------------------------------------------------------------------+
|                                                                   |
|  patternforge/adventures/                                         |
|  |                                                                |
|  +-- __init__.py          # Public API exports                    |
|  |                                                                |
|  +-- models.py            # Data structures                       |
|  |   |                                                            |
|  |   +-- Campaign         # Top-level container                   |
|  |   +-- Chapter          # Group of encounters                   |
|  |   +-- Encounter        # Single challenge                      |
|  |   +-- Choice           # Fork option                           |
|  |   +-- PlayerState      # Progress tracking                     |
|  |   +-- EncounterType    # Skeleton enum                         |
|  |   +-- OutcomeType      # Success/Failure enum                  |
|  |   +-- GameOverOptions  # Recovery options enum                 |
|  |                                                                |
|  +-- state.py             # State machine                         |
|  |   |                                                            |
|  |   +-- AdventureState   # Main controller                       |
|  |       +-- record_outcome()                                     |
|  |       +-- make_choice()                                        |
|  |       +-- retry_from_fork()                                    |
|  |       +-- retry_from_checkpoint()                              |
|  |       +-- start_over()                                         |
|  |       +-- save() / load()                                      |
|  |                                                                |
|  +-- loader.py            # Campaign loading                      |
|      |                                                            |
|      +-- load_campaign()  # YAML -> Campaign                      |
|      +-- validate_campaign()  # Check references                  |
|                                                                   |
+-------------------------------------------------------------------+
```

### 2.2 Data Flow

```
+-------------------------------------------------------------------+
|                       DATA FLOW DIAGRAM                            |
+-------------------------------------------------------------------+
|                                                                   |
|  +-------------+                                                  |
|  | campaign.   |                                                  |
|  | yaml        |                                                  |
|  +------+------+                                                  |
|         |                                                         |
|         v                                                         |
|  +-------------+     +-------------+     +-------------+          |
|  | loader.py   | --> | Campaign    | --> | Adventure   |          |
|  | load_       |     | (validated) |     | State       |          |
|  | campaign()  |     +-------------+     +------+------+          |
|  +-------------+                                |                 |
|                                                 |                 |
|                      +--------------------------|                 |
|                      |                          |                 |
|                      v                          v                 |
|               +-------------+           +-------------+           |
|               | Player      |           | save.json   |           |
|               | Actions     |           | (persist)   |           |
|               +------+------+           +-------------+           |
|                      |                                            |
|                      v                                            |
|               +-------------+                                     |
|               | Outcome     |                                     |
|               | (success/   |                                     |
|               |  failure)   |                                     |
|               +------+------+                                     |
|                      |                                            |
|          +-----------+-----------+                                |
|          |                       |                                |
|          v                       v                                |
|   +-------------+         +-------------+                         |
|   | Continue    |         | Game Over   |                         |
|   | (next       |         | Screen      |                         |
|   |  encounter) |         | (options)   |                         |
|   +-------------+         +------+------+                         |
|                                  |                                |
|                    +-------------+-------------+                  |
|                    |             |             |                  |
|                    v             v             v                  |
|             [Retry Fork] [Retry CP] [Start Over]                  |
|                                                                   |
+-------------------------------------------------------------------+
```

### 2.3 Class Relationships

```
+-------------------------------------------------------------------+
|                   CLASS RELATIONSHIP DIAGRAM                       |
+-------------------------------------------------------------------+
|                                                                   |
|                         +-------------+                           |
|                         |  Campaign   |                           |
|                         +------+------+                           |
|                                |                                  |
|                                | 1:N                              |
|                                v                                  |
|                         +-------------+                           |
|                         |   Chapter   |                           |
|                         +------+------+                           |
|                                |                                  |
|                                | 1:N                              |
|                                v                                  |
|                         +-------------+                           |
|                         |  Encounter  |                           |
|                         +------+------+                           |
|                                |                                  |
|                                | 0:N                              |
|                                v                                  |
|                         +-------------+                           |
|                         |   Choice    |                           |
|                         +-------------+                           |
|                                                                   |
|  +----------------+     +----------------+                        |
|  | AdventureState |---->|  PlayerState   |                        |
|  +-------+--------+     +----------------+                        |
|          |              | - campaign_id  |                        |
|          |              | - chapter_id   |                        |
|          |              | - encounter_id |                        |
|          |              | - xp_earned    |                        |
|          |              | - last_fork    |                        |
|          |              | - last_checkpoint                       |
|          |              | - achievements |                        |
|          |              +----------------+                        |
|          |                                                        |
|          +----> Campaign (reference)                              |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 3. State Machine Design

### 3.1 Core State Transitions

```
+-------------------------------------------------------------------+
|                    STATE MACHINE DIAGRAM                           |
+-------------------------------------------------------------------+
|                                                                   |
|                    +------------------+                           |
|                    |      START       |                           |
|                    +--------+---------+                           |
|                             |                                     |
|                             v                                     |
|                    +------------------+                           |
|             +----->|    ENCOUNTER     |<----+                     |
|             |      +--------+---------+     |                     |
|             |               |               |                     |
|             |      +--------+--------+      |                     |
|             |      |                 |      |                     |
|             |      v                 v      |                     |
|             | +---------+     +-----------+ |                     |
|             | | SUCCESS |     |  FAILURE  | |                     |
|             | +----+----+     +-----+-----+ |                     |
|             |      |                |       |                     |
|             |      v                v       |                     |
|             | +---------+     +-----------+ |                     |
|             | | Award   |     | Game Over | |                     |
|             | | XP      |     | Screen    | |                     |
|             | +----+----+     +-----+-----+ |                     |
|             |      |                |       |                     |
|             |      v                |       |                     |
|             | +---------+           |       |                     |
|             | | Next?   |           |       |                     |
|             | +----+----+           |       |                     |
|             |      |                |       |                     |
|        +----+------+------+         |       |                     |
|        |    |             |         |       |                     |
|        v    v             v         |       |                     |
|  +------+ +------+ +----------+     |       |                     |
|  | Next | |Chapter| | Campaign |    |       |                     |
|  | Enc  | |Complete| Complete |    |       |                     |
|  +--+---+ +---+---+ +----+----+     |       |                     |
|     |         |          |          |       |                     |
|     +---------+          |          |       |                     |
|             |            v          |       |                     |
|             |     +----------+      |       |                     |
|             +---->|   END    |      |       |                     |
|                   +----------+      |       |                     |
|                                     |       |                     |
|             +-----------------------+       |                     |
|             |                               |                     |
|             v                               |                     |
|  +--------------------+                     |                     |
|  | Recovery Options:  |                     |                     |
|  | - Retry Fork    ---+---------------------+                     |
|  | - Retry Checkpoint-+---------------------+                     |
|  | - Start Over    ---+---------------------+                     |
|  | - Leave (exit)     |                                           |
|  +--------------------+                                           |
|                                                                   |
+-------------------------------------------------------------------+
```

### 3.2 Fork Decision Flow

```
+-------------------------------------------------------------------+
|                    FORK DECISION FLOW                              |
+-------------------------------------------------------------------+
|                                                                   |
|                    +------------------+                           |
|                    |  FORK ENCOUNTER  |                           |
|                    |  "Two paths..."  |                           |
|                    +--------+---------+                           |
|                             |                                     |
|                    +--------+--------+                            |
|                    |                 |                            |
|                    v                 v                            |
|             +------------+    +------------+                      |
|             | Choice A   |    | Choice B   |                      |
|             | is_correct |    | is_correct |                      |
|             | = true     |    | = false    |                      |
|             +-----+------+    +-----+------+                      |
|                   |                 |                             |
|                   v                 v                             |
|             +------------+    +------------+                      |
|             | Record     |    | Record     |                      |
|             | last_fork  |    | last_fork  |                      |
|             | choice_    |    | choice_    |                      |
|             | history    |    | history    |                      |
|             +-----+------+    +-----+------+                      |
|                   |                 |                             |
|                   v                 v                             |
|             +------------+    +------------+                      |
|             | Continue   |    | Game Over  |                      |
|             | to success |    | "Darkness  |                      |
|             | path       |    |  claims.." |                      |
|             +------------+    +-----+------+                      |
|                                     |                             |
|                                     v                             |
|                              +------------+                       |
|                              | Retry Fork |                       |
|                              | available  |                       |
|                              +------------+                       |
|                                                                   |
+-------------------------------------------------------------------+
```

### 3.3 Checkpoint & Recovery

```
+-------------------------------------------------------------------+
|                  CHECKPOINT & RECOVERY SYSTEM                      |
+-------------------------------------------------------------------+
|                                                                   |
|  CHECKPOINT CREATION:                                             |
|                                                                   |
|  Encounter with                                                   |
|  is_checkpoint=true  -----> Updates last_checkpoint               |
|         |                                                         |
|         v                                                         |
|  +------------------+                                             |
|  | last_checkpoint  |  Persists across failures                   |
|  | = encounter_id   |  Available in game over options             |
|  +------------------+                                             |
|                                                                   |
|  RECOVERY OPTIONS:                                                |
|                                                                   |
|  +------------------+     +------------------+                    |
|  |  GAME OVER       |     | Available when:  |                    |
|  +------------------+     +------------------+                    |
|  | retry_fork       | <-- | last_fork set    |                    |
|  | retry_checkpoint | <-- | last_checkpoint  |                    |
|  | start_over       | <-- | Always           |                    |
|  | leave            | <-- | Always           |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
|  RECOVERY BEHAVIOR:                                               |
|                                                                   |
|  +------------------+     +------------------+                    |
|  | retry_fork       | --> | Position = fork  |                    |
|  |                  |     | XP preserved     |                    |
|  |                  |     | History kept     |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
|  +------------------+     +------------------+                    |
|  | retry_checkpoint | --> | Position = CP    |                    |
|  |                  |     | XP preserved     |                    |
|  |                  |     | History kept     |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
|  +------------------+     +------------------+                    |
|  | start_over       | --> | Position = start |                    |
|  |                  |     | XP preserved     |                    |
|  |                  |     | Clears last_fork |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 4. Module Characteristics

### 4.1 models.py

| Characteristic | Details |
|----------------|---------|
| **Purpose** | Define data structures for adventures |
| **Dependencies** | pydantic (BaseModel, Field) |
| **Classes** | 8 (Campaign, Chapter, Encounter, Choice, PlayerState, 3 Enums) |
| **Validation** | Pydantic field validation (types, ranges) |
| **Serialization** | JSON via pydantic model_dump() |

**Key Design Decisions:**
- Pydantic for automatic validation and serialization
- Enums for type safety on skeleton types and outcomes
- Optional fields with sensible defaults
- Cross-platform path handling (strings, resolved at load)

### 4.2 state.py

| Characteristic | Details |
|----------------|---------|
| **Purpose** | State machine for player progress |
| **Dependencies** | models.py, json, datetime, pathlib |
| **Classes** | 1 (AdventureState) |
| **Methods** | 12 public methods |
| **State** | Encapsulates PlayerState + Campaign |

**Key Design Decisions:**
- Single class owns all state transitions
- Lookup tables for O(1) encounter access
- Immutable campaign reference
- Optional persistence (save_path can be None)
- UTC timestamps for cross-timezone safety

### 4.3 loader.py

| Characteristic | Details |
|----------------|---------|
| **Purpose** | Load campaigns from YAML files |
| **Dependencies** | yaml, pathlib, models.py |
| **Functions** | 4 (load_campaign, validate_campaign, 2 internal) |
| **Validation** | Reference integrity, duplicate detection |

**Key Design Decisions:**
- YAML for human-readable campaign authoring
- Relative path resolution from campaign file location
- Separate validation function for pre-flight checks
- Graceful handling of optional fields

---

## 5. Test Coverage

### 5.1 Test Categories

```
+-------------------------------------------------------------------+
|                    TEST COVERAGE MATRIX                            |
+-------------------------------------------------------------------+
|                                                                   |
|  Category              | Tests | Status  | Priority              |
|  ----------------------+-------+---------+------------------------|
|  Linear Path (LP)      |   4   | PASS    | P0 Critical           |
|  Fork Path (FP)        |   4   | PASS    | P1 High               |
|  Game Over (GO)        |   6   | PASS    | P0 Critical           |
|  Retry (RT)            |   3   | PASS    | P1 High               |
|  Checkpoint (CP)       |   2   | PASS    | P2 Medium             |
|  Persistence (SP)      |   3   | PASS    | P2 Medium             |
|  Edge Cases (EC)       |   3   | PASS    | P3 Low                |
|  Validation            |   3   | PASS    | P2 Medium             |
|  YAML Loading          |   1   | PASS    | P2 Medium             |
|  ----------------------+-------+---------+------------------------|
|  TOTAL                 |  29   | 100%    |                       |
|                                                                   |
+-------------------------------------------------------------------+
```

### 5.2 Test Execution Results

```
+-------------------------------------------------------------------+
|                    TEST EXECUTION SUMMARY                          |
+-------------------------------------------------------------------+
|                                                                   |
|  Tests Run:        29                                             |
|  Tests Passed:     29                                             |
|  Tests Failed:     0                                              |
|  Tests Skipped:    0                                              |
|                                                                   |
|  Execution Time:   0.09 seconds                                   |
|                                                                   |
|  Coverage:                                                        |
|  +----------------------------------------------------------+    |
|  | adventures/models.py    |████████████████████████| 100%  |    |
|  | adventures/state.py     |████████████████████████| 100%  |    |
|  | adventures/loader.py    |████████████████████████| 100%  |    |
|  +----------------------------------------------------------+    |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 6. Files Created

```
+-------------------------------------------------------------------+
|                    FILES CREATED THIS SPRINT                       |
+-------------------------------------------------------------------+
|                                                                   |
|  Source Code:                                                     |
|  +---------------------------------------------------------+     |
|  | src/patternforge/adventures/__init__.py      |   30 LOC |     |
|  | src/patternforge/adventures/models.py        |  170 LOC |     |
|  | src/patternforge/adventures/state.py         |  280 LOC |     |
|  | src/patternforge/adventures/loader.py        |  140 LOC |     |
|  +---------------------------------------------------------+     |
|  | TOTAL SOURCE                                 |  620 LOC |     |
|  +---------------------------------------------------------+     |
|                                                                   |
|  Tests:                                                           |
|  +---------------------------------------------------------+     |
|  | tests/unit/test_adventures.py                |  450 LOC |     |
|  +---------------------------------------------------------+     |
|                                                                   |
|  Documentation:                                                   |
|  +---------------------------------------------------------+     |
|  | cipher-circle/artifacts/mirth/                          |     |
|  |   game_path_test_plan.md                     |  200 LOC |     |
|  | cipher-circle/roadmaps/                                 |     |
|  |   phase2_pthadventures.md                    |  180 LOC |     |
|  +---------------------------------------------------------+     |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 7. Integration Points

### 7.1 With PatternForge Core

```
+-------------------------------------------------------------------+
|                  INTEGRATION WITH PATTERNFORGE                     |
+-------------------------------------------------------------------+
|                                                                   |
|  PatternForge CLI                                                 |
|       |                                                           |
|       +-- patternforge adventure start <campaign>                 |
|       |       |                                                   |
|       |       +-- Load campaign YAML                              |
|       |       +-- Initialize AdventureState                       |
|       |       +-- Enter encounter loop                            |
|       |                                                           |
|       +-- patternforge adventure resume                           |
|       |       |                                                   |
|       |       +-- Load saved state                                |
|       |       +-- Resume from position                            |
|       |                                                           |
|       +-- patternforge adventure list                             |
|               |                                                   |
|               +-- Show available campaigns                        |
|               +-- Show progress per campaign                      |
|                                                                   |
|  Hash Integration:                                                |
|  +----------------------------------------------------------+    |
|  | Encounter.hash_file --> patternforge attack              |    |
|  | Encounter.solution  --> Verify crack result              |    |
|  | Encounter.expected_time --> Validate designed data       |    |
|  +----------------------------------------------------------+    |
|                                                                   |
+-------------------------------------------------------------------+
```

### 7.2 With Achievement System (Sprint 2.2)

```
+-------------------------------------------------------------------+
|                  INTEGRATION WITH ACHIEVEMENTS                     |
+-------------------------------------------------------------------+
|                                                                   |
|  AdventureState                                                   |
|       |                                                           |
|       +-- record_outcome(SUCCESS)                                 |
|               |                                                   |
|               +-- TRIGGER: "encounter_complete"                   |
|               |       |                                           |
|               |       +-- Check achievement conditions            |
|               |       +-- Award if matched                        |
|               |       +-- Update PlayerState.achievements         |
|               |                                                   |
|               +-- TRIGGER: "chapter_complete"                     |
|               +-- TRIGGER: "campaign_complete"                    |
|               +-- TRIGGER: "first_death"                          |
|               +-- TRIGGER: "retry_success"                        |
|                                                                   |
+-------------------------------------------------------------------+
```

---

## 8. Next Steps

### Sprint 2.1 Remaining
- [ ] CLI integration (`patternforge adventure` command)

### Sprint 2.2: Achievement System
- [ ] Achievement schema
- [ ] Pun library (50+ templates)
- [ ] Trigger system
- [ ] Profile renderer

### Sprint 2.3: Designed Data
- [ ] Tier 0-2 hash sets (instant crack)
- [ ] Tier 3-4 hash sets (quick crack)
- [ ] Data validation tests

### Sprint 2.4: First Campaign
- [ ] The Dread Citadel content
- [ ] 20-25 encounters
- [ ] Full playthrough test

---

## 9. Appendix: Campaign YAML Schema

```yaml
# Campaign YAML Schema Reference

id: string                    # Unique campaign identifier
title: string                 # Display title
description: string           # Campaign overview
version: string               # Semantic version (default: "1.0.0")
author: string                # Author name (default: "The Cipher Circle")
difficulty: string            # Overall difficulty rating
estimated_time: string        # Estimated completion time
intro_text: string            # Opening narrative
outro_text: string            # Completion narrative
first_chapter: string         # Starting chapter ID

chapters:
  - id: string                # Unique chapter identifier
    title: string             # Display title
    description: string       # Chapter overview
    first_encounter: string   # Starting encounter ID
    intro_text: string        # Chapter opening
    outro_text: string        # Chapter completion

    encounters:
      - id: string            # Unique encounter identifier
        title: string         # Display title
        type: string          # Skeleton type (flash, fork, etc.)
        tier: integer         # Difficulty (0-6)
        xp_reward: integer    # Grains of sand (default: 10)

        # Narrative
        intro_text: string    # Encounter opening
        success_text: string  # On success
        failure_text: string  # On failure (game over)
        objective: string     # What player must do
        hint: string          # Optional hint
        solution: string      # Expected answer

        # Data
        hash_file: string     # Path to hash file
        wordlist: string      # Suggested wordlist
        expected_time: integer # Expected crack time (seconds)

        # Flow
        next_encounter: string # Next encounter ID (linear)
        is_checkpoint: boolean # Safe respawn point

        # Choices (for fork type)
        choices:
          - id: string        # Choice identifier
            label: string     # Display text
            description: string
            leads_to: string  # Target encounter ID
            is_correct: boolean # Success path?
```

---

*Report generated by The Cipher Circle*
*Sprint 2.1 - Adventure State Machine*
*2026-01-24*
