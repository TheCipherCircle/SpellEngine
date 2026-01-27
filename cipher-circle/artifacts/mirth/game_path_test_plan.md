# Game Path Test Plan

*Designed by Mirth, The Gamewright*
*For: PTHAdventures QA*

---

## Overview

This test plan validates adventure paths, fork logic, and game over flows.
Tests should be automated once the state machine is built.

---

## Test Categories

### 1. Linear Path Tests
**Purpose:** Verify basic encounter-to-encounter progression

| Test ID | Description | Expected |
|---------|-------------|----------|
| LP-01 | Complete first encounter, advance to second | State shows encounter #2 |
| LP-02 | Complete all encounters in chapter | Chapter marked complete |
| LP-03 | Complete all chapters | Campaign marked complete |
| LP-04 | XP accumulates across encounters | Total XP = sum of rewards |
| LP-05 | Completed encounters tracked in history | List contains all passed |

### 2. Fork Path Tests
**Purpose:** Verify branching logic works correctly

| Test ID | Description | Expected |
|---------|-------------|----------|
| FP-01 | Choose correct path at fork | Advance to success branch |
| FP-02 | Choose wrong path at fork | Trigger game over |
| FP-03 | Fork recorded in last_fork | State tracks fork ID |
| FP-04 | Choice recorded in history | choice_history has entry |
| FP-05 | Multiple forks track latest | last_fork = most recent |

### 3. Game Over Tests
**Purpose:** Verify failure handling and recovery options

| Test ID | Description | Expected |
|---------|-------------|----------|
| GO-01 | Failure triggers game over | Action = "game_over" |
| GO-02 | Death counter increments | deaths += 1 |
| GO-03 | Options include retry_fork (if fork exists) | retry_fork in options |
| GO-04 | Options include retry_checkpoint (if exists) | retry_checkpoint in options |
| GO-05 | Options always include start_over | start_over in options |
| GO-06 | Options always include leave | leave in options |

### 4. Retry Tests
**Purpose:** Verify recovery flows work correctly

| Test ID | Description | Expected |
|---------|-------------|----------|
| RT-01 | Retry from fork restores position | encounter_id = fork_id |
| RT-02 | Retry from checkpoint restores position | encounter_id = checkpoint_id |
| RT-03 | Start over resets to chapter start | encounter_id = first_encounter |
| RT-04 | XP preserved on retry | xp_earned unchanged |
| RT-05 | Completed encounters preserved | history unchanged |

### 5. Checkpoint Tests
**Purpose:** Verify checkpoint system works

| Test ID | Description | Expected |
|---------|-------------|----------|
| CP-01 | Completing checkpoint updates last_checkpoint | State has checkpoint ID |
| CP-02 | Non-checkpoint doesn't update | last_checkpoint unchanged |
| CP-03 | Multiple checkpoints track latest | last_checkpoint = newest |
| CP-04 | Checkpoint persists across failures | Available after game over |

### 6. State Persistence Tests
**Purpose:** Verify save/load works correctly

| Test ID | Description | Expected |
|---------|-------------|----------|
| SP-01 | Save creates file | File exists at save_path |
| SP-02 | Load restores position | Same encounter_id |
| SP-03 | Load restores history | Same completed_encounters |
| SP-04 | Load restores XP | Same total_xp |
| SP-05 | Load restores achievements | Same achievements list |
| SP-06 | Save handles missing directory | Creates parent dirs |

### 7. Edge Case Tests
**Purpose:** Handle unusual situations gracefully

| Test ID | Description | Expected |
|---------|-------------|----------|
| EC-01 | Invalid choice at fork | Error action, helpful message |
| EC-02 | Retry fork with no fork history | Error action |
| EC-03 | Retry checkpoint with no checkpoint | Error action |
| EC-04 | Empty campaign loads | Validation errors list |
| EC-05 | Circular references detected | Validation warns |
| EC-06 | Missing encounter reference | Validation errors |

### 8. Cross-Platform Tests
**Purpose:** Verify works on all target platforms

| Test ID | Description | Platform | Expected |
|---------|-------------|----------|----------|
| XP-01 | Path handling | Windows | Paths resolve correctly |
| XP-02 | Path handling | macOS | Paths resolve correctly |
| XP-03 | Path handling | Linux | Paths resolve correctly |
| XP-04 | YAML loading | All | UTF-8 content loads |
| XP-05 | State save/load | All | JSON round-trips |

---

## Test Data Requirements

### Minimal Test Campaign
```yaml
id: test_campaign
title: Test Campaign
first_chapter: ch1

chapters:
  - id: ch1
    title: Test Chapter
    first_encounter: enc1
    encounters:
      - id: enc1
        title: First Encounter
        type: flash
        next_encounter: enc2

      - id: enc2
        title: Fork Encounter
        type: fork
        choices:
          - id: correct
            label: Right Path
            leads_to: enc3
            is_correct: true
          - id: wrong
            label: Wrong Path
            leads_to: enc_fail
            is_correct: false

      - id: enc3
        title: Checkpoint
        type: flash
        is_checkpoint: true
        next_encounter: enc4

      - id: enc4
        title: Final Encounter
        type: flash

      - id: enc_fail
        title: Failure Point
        type: flash
```

### Edge Case Campaign
- Empty chapters list
- Circular next_encounter references
- Invalid encounter type
- Missing required fields

---

## Automation Notes

### Test Framework
- Use pytest with fixtures
- Create reusable campaign fixtures
- Mock file I/O for persistence tests

### CI Integration
- Run on push to adventure-related paths
- Cross-platform matrix: ubuntu, macos, windows
- Report coverage for adventures module

### Regression Testing
- After each sprint, run full test plan
- Any new skeleton type needs path tests
- Any new game over option needs recovery tests

---

## Test Priority

| Priority | Category | Rationale |
|----------|----------|-----------|
| P0 (Critical) | Linear Path, Game Over | Core functionality |
| P1 (High) | Fork Path, Retry | Main player experience |
| P2 (Medium) | Checkpoint, Persistence | Quality of life |
| P3 (Low) | Edge Cases, Cross-Platform | Polish |

---

*Mirth says: "Every path must be tested. Every death must be recoverable. Every choice must matter."*
