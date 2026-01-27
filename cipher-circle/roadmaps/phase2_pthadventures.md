# Phase 2: PTHAdventures Foundation

*The Cipher Circle builds the adventure system*

**STATUS: ✅ COMPLETE** (as of 2026-01-25)

---

## Overview

**Goal:** Build the foundation for choose-your-own-adventure password cracking education.

**Core Systems:**
1. ✅ Adventure state machine (position, forks, continuity)
2. ✅ Achievement system (triggers, puns, profiles)
3. ✅ Designed data sets (working exercises)
4. ✅ First campaign content (The Dread Citadel)

---

## Sprint Breakdown

### Sprint 2.1: State Machine & Structure ✅ COMPLETE
**Focus:** The bones of the adventure system

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Define adventure schema | Forge | ✅ | YAML structure for campaigns, chapters, encounters |
| Implement state tracker | Forge | ✅ | AdventureState class, position, history |
| Fork/retry logic | Forge | ✅ | Game over → retry from fork / checkpoint / leave |
| CLI integration | Forge | ✅ | `patternforge adventure`, `rogue`, `game`, `twocovers` |

**Deliverables:**
- `src/patternforge/adventures/models.py` - Campaign, Chapter, Encounter, Choice
- `src/patternforge/adventures/state.py` - AdventureState machine
- `src/patternforge/adventures/loader.py` - YAML campaign loading
- 29 unit tests

---

### Sprint 2.2: Achievement System ✅ COMPLETE
**Focus:** Puns, progress, personality

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Achievement schema | Mirth | ✅ | Pydantic models with triggers |
| Pun library | Mirth | ✅ | **55 achievements** across categories |
| Trigger system | Forge | ✅ | Event → achievement mapping |
| Profile renderer | Mirth | ✅ | Stats + achievements display |

**Achievement Categories:**
- Hash puns (md5, sha, bcrypt, etc.) ✅
- Crack puns (broke, cracked, shattered) ✅
- Crypto puns (salt, pepper, rainbow) ✅
- Tool puns (hashcat, john, masks) ✅
- Progress puns (levels, xp, grains of sand) ✅

**Deliverables:**
- `src/patternforge/adventures/achievements.py` - 986 lines, 55 puns
- 62 unit tests

---

### Sprint 2.3: Designed Data ✅ COMPLETE
**Focus:** Exercises that WORK QUICKLY

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Tier 0-2 hash sets | Forge | ✅ | Instant-crack designed data |
| Tier 3-4 hash sets | Forge | ✅ | Quick-crack with right approach |
| Tier 5-6 hash sets | Forge | ✅ | Progressive/challenge data |
| Data validation | Anvil | ✅ | All hashes crack as expected |
| Hashcat integration | Forge | ✅ | Attack commands per exercise |

**Design Principles:**
- Tier 0-2: < 1 second crack time ✅
- Tier 3-4: < 30 seconds with correct approach ✅
- Tier 5-6: Teaches iteration/progressive attacks ✅
- ALL data reproducible and tested ✅

**Deliverables:**
- `src/patternforge/adventures/hashlib_designed.py` - 882 lines, **70 hashes**
- `DREAD_CITADEL_HASH_MAP` - All campaign hashes mapped
- 49 unit tests

---

### Sprint 2.4: First Campaign - The Dread Citadel ✅ COMPLETE
**Focus:** Actual playable content

| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Campaign outline | Mirth | ✅ | 3 chapters, boss fight |
| Chapter 1: The Outer Gates | Mirth | ✅ | 8 encounters, intro difficulty |
| Chapter 2: The Crypts | Mirth | ✅ | 10 encounters, pattern focus |
| Chapter 3: The Inner Sanctum | Mirth | ✅ | 6 encounters, SHA-1 finale |
| Final Boss: Citadel Lord | Mirth | ✅ | Capstone SHA-1 challenge |
| Narrative flavor | Loreth | ✅ | Intro text, transitions, victory |
| Hashtopia clue links | Loreth | ✅ | 31 encounters → knowledge base |

**Skeleton Distribution (Actual):**
- FLASH: 15 encounters (48%) - Quick challenges
- TOUR: 13 encounters (42%) - Guided learning
- FORK: 2 encounters (7%) - Player choice
- GAMBIT: 1 encounter (3%) - Risk/reward

**Deliverables:**
- `src/patternforge/campaigns/dread_citadel.yaml` - 24 encounters, 3 chapters
- 82/82 QA tests passing
- Full playthrough validated

---

## Bonus Content (Dragon Slaying Session)

### Two Covers UI ✅ COMPLETE
| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Side-by-side layout | Forge | ✅ | Story + Craft panels |
| Wizard mode | Forge | ✅ | 3-step guided workflow |
| Shell mode | Forge | ✅ | Expert REPL interface |
| CLI integration | Forge | ✅ | `patternforge twocovers` |

**Deliverables:**
- `src/patternforge/cli/two_covers.py` - 959 lines
- 17 smoke tests

### Dice Rolling System ✅ COMPLETE
| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Polyhedral dice | Forge | ✅ | d4, d6, d8, d10, d12, d20, d100 |
| ASCII art | Forge | ✅ | Visual dice faces |
| Animation | Forge | ✅ | Tumbling dice effect |
| Game mechanics | Forge | ✅ | skill_check, loot_roll, oracle |

**Deliverables:**
- `src/patternforge/adventures/dice.py` - 448 lines
- `src/patternforge/cli/roll.py` - CLI command

### Experience Grading System ✅ COMPLETE
| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| Grading dimensions | Mirth | ✅ | 8 dimensions (clarity, engagement, etc.) |
| Narrative layers | Mirth | ✅ | 5 context layers (individual → meta) |
| Campaign grades | Mirth | ✅ | All Dread Citadel encounters graded |
| Player feedback | Mirth | ✅ | Opt-in feedback collection |

**Deliverables:**
- `src/patternforge/adventures/experience_grading.py` - 2,764 lines
- `src/patternforge/campaigns/dread_citadel_grades.yaml`
- 64 unit tests

---

## Success Criteria ✅ ALL MET

Phase 2 is DONE when:
- [x] Player can start The Dread Citadel
- [x] State persists across sessions
- [x] Wrong choices hit game over with retry options
- [x] Achievements earned and displayed
- [x] All exercises crack in expected time
- [x] 20+ encounters playable end-to-end (we have 24!)
- [x] Full QA validation (82/82 tests)
- [x] Hashtopia knowledge base linked (31 encounters)

---

## XP Awards (Phase 2) ✅ EARNED

| Milestone | Grains | Status |
|-----------|--------|--------|
| Sprint 2.1 complete | 50 | ✅ |
| Sprint 2.2 complete | 50 | ✅ |
| Sprint 2.3 complete | 75 | ✅ |
| Sprint 2.4 complete | 100 | ✅ |
| First full playthrough | 50 | ✅ |
| Phase 2 shipped | 200 | ✅ |
| **TOTAL** | **525** | ✅ |

---

## Final Stats

| Metric | Value |
|--------|-------|
| Total Tests | 924 |
| Lines Added | 5,000+ |
| Encounters | 31 |
| Achievements | 55 |
| Designed Hashes | 70 |
| Party Members | 8 |
| Grains Earned | 1,577 |

---

*Completed by the Cipher Circle, 2026-01-25*
*"We worked hard. We had fun. We did amazing things."*
