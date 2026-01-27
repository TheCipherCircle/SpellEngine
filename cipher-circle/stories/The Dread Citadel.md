---
tags:
  - quest/campaign
  - quest/validated
  - difficulty/beginner
  - hash/md5
  - hash/sha1
  - technique/wordlist
  - technique/mask
  - status/approved
  - pthadventures
created: 2026-01-24
---

# Campaign Design: The Dread Citadel

## Overview

**Target**: Complete beginners (no prior hash cracking knowledge)
**Theme**: Dark fortress infiltration - gates, crypts, final boss
**Hash Types**: MD5, SHA1
**Techniques**: Wordlists, Masks
**Estimated Time**: 45-60 minutes
**Encounters**: ~22-25 total across 3 chapters

---

## Narrative Arc

The player is a novice infiltrator approaching the Dread Citadel, a fortress protected by cryptographic locks. Each gate requires cracking password hashes to proceed. The deeper you go, the stronger the defenses.

**Tone**: Mysterious, slightly foreboding, but encouraging. The "Cipher Circle" guides the player as a mentor voice.

---

## Chapter Structure

### Chapter 1: The Outer Gates (7-8 encounters)
**Goal**: Understand what hashes are, crack first MD5 hashes with wordlists

| # | Type | Title | Purpose | Tier |
|---|------|-------|---------|------|
| 1 | TOUR | The Approach | Narrative intro, what lies ahead | 0 |
| 2 | TOUR | What Guards These Gates | Explain hashes - one-way functions | 0 |
| 3 | FLASH | The First Lock | Crack "password" MD5 with hint | 0 |
| 4 | TOUR | The Wordsmith's Wisdom | Explain wordlists - collections of known passwords | 0 |
| 5 | FLASH | The Common Tongue | Crack "123456" MD5 - most common password | 0 |
| 6 | FLASH | The Servant's Key | Crack "admin" MD5 | 1 |
| 7 | CHECKPOINT | The Inner Threshold | Reflect on wordlist power, checkpoint | 0 |
| 8 | FLASH | The Gatekeeper's Challenge | Slightly harder - "letmein" or similar | 1 |

**Learning outcomes**:
- Hashes are one-way transformations
- Cracking = guessing + comparing
- Common passwords are easily cracked
- Wordlists contain known passwords

---

### Chapter 2: The Crypts (9-10 encounters)
**Goal**: Learn mask attacks, encounter SHA1, understand algorithm differences

| # | Type | Title | Purpose | Tier |
|---|------|-------|---------|------|
| 1 | TOUR | Descending | Narrative transition, harder locks ahead | 0 |
| 2 | TOUR | The Pattern Weaver | Introduce masks - ?l ?u ?d ?s notation | 0 |
| 3 | FLASH | Simple Patterns | Crack 4-digit PIN (MD5 of "1234") | 1 |
| 4 | FLASH | The Name Game | Crack "Name1234" pattern - ?u?l?l?l?d?d?d?d | 1 |
| 5 | FORK | The Crossroads | Choose: wordlist chamber vs mask forge | 1 |
| 5a | FLASH | (Wordlist path) The Ancient Scroll | Crack using intuition/wordlist thinking | 2 |
| 5b | FLASH | (Mask path) The Pattern Lock | Crack using mask thinking | 2 |
| 6 | TOUR | A Different Cipher | Introduce SHA1 - same concept, different algorithm | 0 |
| 7 | FLASH | SHA1's First Test | Crack simple SHA1 hash | 1 |
| 8 | GAMBIT | The Trapped Chest | **RISK/REWARD**: Safe path = easy hash (15 XP), Risky = harder hash (30 XP) | 2 |
| 9 | CHECKPOINT | The Deep Archive | Reflect on masks vs wordlists, checkpoint | 0 |
| 10 | FLASH | The Crypt Guardian | Harder SHA1 crack - combines learning | 2 |

**Learning outcomes**:
- Masks generate candidates from patterns
- ?l = lowercase, ?u = uppercase, ?d = digit, ?s = special
- SHA1 is different algorithm, same cracking approach
- Wordlists = known words, Masks = unknown patterns
- Risk assessment in attack selection

---

### Chapter 3: The Inner Sanctum (6-7 encounters)
**Goal**: Combine skills, face the boss, earn victory

| # | Type | Title | Purpose | Tier |
|---|------|-------|---------|------|
| 1 | TOUR | The Final Ascent | Narrative buildup, all skills needed | 0 |
| 2 | FLASH | The Left Hand | MD5 crack requiring wordlist thinking | 2 |
| 3 | FLASH | The Right Hand | SHA1 crack requiring mask thinking | 2 |
| 4 | FORK | The Lord's Chamber | Choose approach for boss: wordlist or mask | 2 |
| 5 | FLASH | **The Citadel Lord** (BOSS) | Multi-step: identify algorithm + crack | 3 |
| 6 | TOUR | Victory | Celebration, summary of skills learned | 0 |
| 7 | TOUR | What Lies Beyond | Tease future: rules, bcrypt, rainbow tables | 0 |

**Learning outcomes**:
- Combine algorithm identification + attack selection
- Confidence in basic cracking workflow
- Awareness of what's next to learn

---

## Encounter Type Distribution

| Type | Count | % |
|------|-------|---|
| TOUR | 10 | 42% |
| FLASH | 11 | 46% |
| FORK | 2 | 8% |
| GAMBIT | 1 | 4% |
| **Total** | 24 | 100% |

For complete beginners, heavy TOUR usage (42%) ensures concepts are explained before challenges. FLASH encounters (46%) provide immediate feedback. Two FORKs give player agency. One GAMBIT introduces risk/reward thinking.

---

## Test Data Requirements

All hashes must be pre-computed and verified. Need:

### MD5 Hashes
| Password | Hash | Encounter |
|----------|------|-----------|
| password | 5f4dcc3b5aa765d61d8327deb882cf99 | Ch1: First Lock |
| 123456 | e10adc3949ba59abbe56e057f20f883e | Ch1: Common Tongue |
| admin | 21232f297a57a5a743894a0e4a801fc3 | Ch1: Servant's Key |
| letmein | 0d107d09f5bbe40cade3de5c71e9e9b7 | Ch1: Gatekeeper |
| 1234 | 81dc9bdb52d04dc20036dbd8313ed055 | Ch2: Simple Patterns |
| John2024 | (to compute) | Ch2: Name Game |

### SHA1 Hashes
| Password | Hash | Encounter |
|----------|------|-----------|
| hello | aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d | Ch2: SHA1 First Test |
| secret | e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4 | Ch2: Crypt Guardian |
| (boss password) | (to compute) | Ch3: Boss |

---

## Checkpoint Placement

1. **Ch1: The Inner Threshold** (after encounter 7) - Before gatekeeper challenge
2. **Ch2: The Deep Archive** (after encounter 8) - Before crypt guardian
3. **Ch3: Before boss** (implicit via fork)

Players can recover to these points on failure.

---

## XP Rewards

| Encounter Type | Base XP |
|----------------|---------|
| TOUR (intro) | 5 |
| TOUR (concept) | 10 |
| FLASH (tier 0-1) | 15 |
| FLASH (tier 2) | 20 |
| FLASH (tier 3/boss) | 30 |
| FORK | 10 |

**Total possible**: ~300 XP

---

## Files to Create

1. `src/patternforge/campaigns/dread_citadel.yaml` - Campaign definition
2. `tests/unit/test_dread_citadel.py` - Validation tests
3. Update tutorial.yaml references if needed

---

## Verification Plan

1. Run `validate_campaign()` on the YAML
2. Test all hash solutions are correct
3. Smoke test: `patternforge adventure list` shows campaign
4. Smoke test: `patternforge adventure start dread_citadel`
5. Manual playthrough of all paths

---

## Design Decisions (Resolved)

1. **Boss format**: FLASH - single challenge (identify algorithm + crack). Clean and satisfying.
2. **GAMBIT**: Added in Chapter 2 - "The Trapped Chest" risk/reward encounter.
3. **Password theme**: Real-world common passwords (password, 123456, admin, etc.) - authentic breach data patterns for maximum educational value.
4. **Narrative tone**: 80% B+C blend (atmospheric tension with real stakes), 20% light moments for levity.
   - B = "The ward rejects your offering. The guardians stir in their crypts..."
   - C = "Your intrusion has been noted. The Citadel's eyes turn toward you."
   - A (occasional) = Skeleton with note: "Password was 'password'. I was so close."
5. **Data philosophy**: Exercise data and challenge data both use real-world breach patterns. Training value = authentic recognition skills that transfer to actual password cracking.

## Remaining Decisions

1. Exact passwords for GAMBIT safe/risky paths
2. Boss encounter password selection

---

## Failure States & Hint System

### Failure Flow

| Attempt | Response |
|---------|----------|
| 1-2 | Atmospheric failure message ("The lock holds.") |
| 3 | **HINT** - Clue + Hashtopia link |
| 4 | Additional hint available |
| 5 | **WALKTHROUGH** - Full solution with copy-paste commands |

### Hint Format

```
The Pattern Weaver whispers: "This lock follows a pattern...
four letters, four numbers. Masks can forge such keys."

Learn more: hashtopia.net → I Want to Learn Methodology → Masks
```

Hints link to relevant Hashtopia learning paths:
- Hash identification → "I Have a Hash to Crack"
- Technique selection → "I Want to Learn Methodology"
- Tool usage → "I Need a Tool"
- Specific topics → Direct page links (Hash Types, Masks, Wordlists, etc.)

### Walkthrough Format

```
The Cipher Circle intervenes...

Solution:
> hashcat -m 0 -a 3 hash.txt ?l?l?l?l?d?d?d?d

[Copy to clipboard]

Why this works: The password follows a Name+Year pattern.
Masks generate all combinations matching this structure.
```

### Walkthrough Access

| Mode | Access Method |
|------|---------------|
| Game (pygame) | F1 key |
| Shell | `walkthrough` or `help` command |
| CLI | Not needed (power users) |

---

## XP System

### Base XP Values

| Encounter Type | Base XP |
|----------------|---------|
| TOUR (intro) | 5 |
| TOUR (concept) | 10 |
| FLASH (tier 0-1) | 15 |
| FLASH (tier 2) | 20 |
| FLASH (tier 3/boss) | 30 |
| FORK | 10 |
| GAMBIT (safe) | 15 |
| GAMBIT (risky success) | 30 |

### XP Modifiers

| Scenario | XP Modifier |
|----------|-------------|
| Clean solve | 100% |
| 1 hint used | 90% |
| 2 hints used | 80% |
| 3 hints used | 70% |
| Walkthrough used | 10% |

**Total possible XP**: ~300
**Minimum completion XP**: ~30 (all walkthroughs)

---

## Adventure Report

Generated at campaign completion. Tracks struggles and creates personalized learning plan.

### Report Format

```
═══════════════════════════════════════════════
         THE DREAD CITADEL - COMPLETE
═══════════════════════════════════════════════

 Encounters Cleared:  24/24
 Total XP Earned:     247/300 (82%)
 Clean Solves:        18
 Hints Used:          9
 Walkthroughs Used:   1

───────────────────────────────────────────────
         YOUR LEARNING PLAN
───────────────────────────────────────────────

 Based on where you needed help:

 □ Mask Attacks (3 hints used)
   → hashtopia.net/8. Masks/Masks
   → hashtopia.net/8. Masks/Mask Attack Strategy

 □ SHA1 Identification (2 hints used)
   → hashtopia.net/10. Cryptographic Hash Algorithms/Hash Types

 □ Wordlist Selection (1 walkthrough)
   → hashtopia.net/7. Wordlists/Wordlists and Dictionaries

───────────────────────────────────────────────
 "Return stronger, infiltrator."
═══════════════════════════════════════════════
```

### Data Tracked for Report

- Encounters completed (with timestamps)
- Hints used per encounter (with topic tags)
- Walkthroughs used per encounter
- XP earned vs possible
- Topic struggle scores (hints/walkthroughs aggregated by topic)

### Hashtopia Integration

Each hint/walkthrough is tagged with relevant Hashtopia topics:
- `mask_attacks`
- `wordlist_selection`
- `hash_identification`
- `algorithm_differences`
- `attack_strategy`

Report aggregates these tags to generate learning plan links.

---

## Agent Notes

### Explore Agent (a9adb48)
- Documented all 15 encounter types with use cases
- Mapped state machine capabilities: forks, checkpoints, game over recovery options
- Identified skeleton distribution target from phase 2 roadmap: 30/30/20/20 split
- Tutorial campaign uses 3 encounter types (TOUR, FLASH, FORK) as reference pattern
- Recommended starting with ~5-7 encounters per chapter for pacing

### Design Considerations
- Heavy TOUR usage (42%) appropriate for complete beginners - explains before challenges
- GAMBIT placement in Chapter 2 introduces risk/reward after basics established
- Real-world passwords maximize educational transfer to actual breach analysis
- Checkpoint placement enables recovery without excessive replay frustration
