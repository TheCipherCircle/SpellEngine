# Art Health Check Report

**Date:** 2026-01-25
**Author:** Fraz + Forge
**Status:** Audit Complete

---

## Executive Summary

**Finding:** PatternForge has ASCII art infrastructure but NO actual image files for pygame mode. The team portrait and pixel art mentioned in planning docs were never created - they remain TODO items.

| Asset Type | Status | Count |
|------------|--------|-------|
| ASCII Art (registered) | Working | 18 pieces |
| ASCII Art (used in code) | Partial | 4 of 18 actively used |
| Pygame Images | MISSING | 0 files |
| Team Portrait | NEVER CREATED | TODO |

---

## 1. ASCII Art Inventory

### Registered Art Pieces (18 total)

| Art ID | Category | Used In Code | Status |
|--------|----------|--------------|--------|
| `CLI_BANNER` | Branding | CLI help | Active |
| `CITADEL_LORD` | Characters | Two Covers | Active |
| `GATEKEEPER` | Characters | Two Covers | Active |
| `VICTORY` | Status | Two Covers, Adventure | Active |
| `DEFEAT` | Status | NOT USED | Orphaned |
| `TREASURE` | Status | NOT USED | Orphaned |
| `GAME_OVER` | Death | NOT USED | NEW - Needs wiring |
| `LOCKED_OUT` | Death | NOT USED | NEW - Needs wiring |
| `CHALLENGE_FAILED` | Death | NOT USED | NEW - Needs wiring |
| `LOCK_TIER_1` | Locks | NOT USED | Orphaned |
| `LOCK_TIER_2` | Locks | NOT USED | Orphaned |
| `LOCK_TIER_3` | Locks | NOT USED | Orphaned |
| `LOCK_TIER_4` | Locks | NOT USED | Orphaned |
| `LOCK_TIER_5` | Locks | NOT USED | Orphaned |
| `LOCK_TIER_6` | Locks | NOT USED | Orphaned |
| `THE_OUTER_GATES` | Chapters | NOT USED | Orphaned |
| `THE_CRYPTS` | Chapters | NOT USED | Orphaned |
| `THE_INNER_SANCTUM` | Chapters | NOT USED | Orphaned |

### Usage Analysis

**Actively Used (4):**
- `CLI_BANNER` - Displayed in CLI help
- `CITADEL_LORD` - Two Covers final boss
- `GATEKEEPER` - Two Covers gate encounters
- `VICTORY` - Two Covers win screen

**Orphaned - Never Connected (14):**
- Death screens (DEFEAT, GAME_OVER, LOCKED_OUT, CHALLENGE_FAILED)
- Lock tiers (LOCK_TIER_1 through LOCK_TIER_6)
- Chapter banners (THE_OUTER_GATES, THE_CRYPTS, THE_INNER_SANCTUM)
- TREASURE

---

## 2. Pygame Mode Images

### Expected Asset Structure

```
assets/
└── images/
    ├── dread_citadel/           # Campaign images
    │   ├── outer_gates_card.png # Chapter cards (512x256)
    │   ├── crypts_card.png
    │   ├── inner_sanctum_card.png
    │   ├── gate_1.png           # Encounter images (512x384)
    │   ├── gate_2.png
    │   ├── crypt_1.png
    │   └── ...
    └── badges/                   # Achievement badges (64x64)
        ├── first_crack.png
        ├── speed_demon.png
        └── ...
```

### Current Reality

```
assets/
└── images/
    └── dread_citadel/           # EXISTS but EMPTY
        └── (no files)
```

**Result:** Pygame mode (`patternforge play --game`) displays PLACEHOLDER GRAPHICS - gray boxes with diagonal lines and text labels. No actual art exists.

### Placeholder Generation

The `AssetLoader` class in `src/patternforge/adventures/assets.py` generates placeholders:

```python
def _create_placeholder(self, width: int, height: int, label: str):
    # Creates gray box with diagonal lines and label text
    # Gruvbox colors: bg #282828, border #504945
```

This is by design for development, but means **pygame mode has no real art**.

---

## 3. Team Portrait / Pixel Art

### Status: NEVER CREATED

The following items from planning documents were **never implemented**:

| Planned Item | Location | Status |
|--------------|----------|--------|
| Cipher Circle team portrait | cipher-circle/ | NOT CREATED |
| Fraz pixel art | cipher-circle/ | NOT CREATED |
| D&D character cards | cipher-circle/ | NOT CREATED |
| README hero banner | README.md | NOT CREATED |
| Architecture diagram | README.md | NOT CREATED |

These were Sprint 2 tasks that remain TODO. The cipher-circle git has:
- Documentation (voice guides, profiles, interviews)
- ASCII art in code
- NO image files

---

## 4. Code Integration Gaps

### Two Covers Mode (`src/patternforge/cli/two_covers.py`)

**Current art usage:**
```python
def get_encounter_art(encounter_type: str, tier: int) -> str:
    if encounter_type == "gate":
        return get_art("GATEKEEPER")  # Always same art
    elif encounter_type == "boss":
        return get_art("CITADEL_LORD")
    elif encounter_type == "victory":
        return get_art("VICTORY")
    return ""  # Most encounters have NO art
```

**Missing connections:**
- `LOCK_TIER_*` not used for difficulty visualization
- `DEFEAT` not shown on failure
- `GAME_OVER`, `LOCKED_OUT`, `CHALLENGE_FAILED` not wired
- Chapter banners not displayed

### Recommended Fixes

```python
# Example: Add lock art based on tier
def get_encounter_art(encounter_type: str, tier: int) -> str:
    if encounter_type == "hash_crack":
        return get_lock_for_tier(min(tier, 6))  # Use lock art
    elif encounter_type == "gate":
        return get_art("GATEKEEPER")
    elif encounter_type == "boss":
        return get_art("CITADEL_LORD")
    elif encounter_type == "victory":
        return get_art("VICTORY")
    return ""

# Example: Add failure art
def get_failure_art(failure_type: str) -> str:
    if failure_type == "game_over":
        return get_art("GAME_OVER")
    elif failure_type == "locked_out":
        return get_art("LOCKED_OUT")
    else:
        return get_art("CHALLENGE_FAILED")
```

---

## 5. Art Samples (ASCII)

### CLI_BANNER (Active)
```
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▓█
  ░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█
  ▓   ██████   █████  ████████ ████████ ███████ ██████  ███  █
  ...
```

### LOCK_TIER_1 (Orphaned - not used)
```
           ╭───────────╮
           │  ┌─────┐  │
           │  │ ◊◊◊ │  │
           │  │ ◊◊◊ │  │
           │  └──┬──┘  │
           │     │     │
           ╰─────┴─────╯
            TIER 1 LOCK
```

### GAME_OVER (New - not wired)
```
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
        █░░░░░░░░░░░░░░░░░░░░░░░█
        █░░▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄░░░█
        █░█  ████   ████  █░░░█
        █░█  ████   ████  █░░░█
        █░█                █░░░█
        █░█   ▀▀▀▀▀▀▀▀▀   █░░░█
        █░░▀▄▄▄▄▄▄▄▄▄▄▄▄▄▀░░░░█
        █░░░░░░░░░░░░░░░░░░░░░░█
        ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
             GAME  OVER
```

---

## 6. Recommendations

### Immediate (Wire existing art)

1. **Connect lock tiers to encounters**
   - Display `LOCK_TIER_N` based on encounter difficulty
   - File: `src/patternforge/cli/two_covers.py`

2. **Wire death screens**
   - Use `GAME_OVER` for campaign failure
   - Use `LOCKED_OUT` for too many failed attempts
   - Use `CHALLENGE_FAILED` for individual encounter failure

3. **Display chapter banners**
   - Show `THE_OUTER_GATES` etc. at chapter transitions

### Short-term (Create missing assets)

1. **Pygame placeholder images** (optional)
   - Create actual .png files for dread_citadel encounters
   - Or accept placeholders as intentional "retro" aesthetic

2. **Team portrait**
   - Create pixel art of 9-member Cipher Circle
   - Place in `cipher-circle/` or `assets/`

### Long-term

1. **Full art pipeline**
   - Image generation workflow
   - Consistent style guide
   - Asset management

---

## 7. Action Items

| Priority | Task | Owner | Effort |
|----------|------|-------|--------|
| HIGH | Wire LOCK_TIER_* to encounters | Forge | 1 hour |
| HIGH | Wire death screens | Forge | 30 min |
| HIGH | Wire chapter banners | Forge | 30 min |
| MEDIUM | Create team portrait | Fraz | 2-4 hours |
| MEDIUM | Create README graphics | Prism | 2-4 hours |
| LOW | Create pygame encounter images | Fraz | 8+ hours |

---

## 8. Conclusion

**The art exists but isn't fully connected.** PatternForge has 18 ASCII art pieces but only uses 4. The new death screens (GAME_OVER, LOCKED_OUT, CHALLENGE_FAILED) need to be wired into the game logic.

**The team portrait was never created.** This was a Sprint 2 planning item that remained TODO. There are no pixel art or image files in the cipher-circle directory.

**Pygame mode uses placeholders by design.** The asset loader generates gray placeholder boxes when images don't exist, which is the current state for all pygame graphics.

---

*Report generated by Forge + Fraz Art Audit*
