# Work Order: Art Polish & Integration

**Assigned to:** Fraz, The Pigment Alchemist
**Priority:** High
**Status:** ✅ COMPLETE (2026-01-25)

---

## Context

The ascii_art.py library is largely complete with excellent pieces:
- CLI_BANNER, CITADEL_LORD, GATEKEEPER (characters)
- VICTORY, DEFEAT, TREASURE (status screens)
- LOCK_TIER_1-6 (full progression)
- THE_OUTER_GATES, THE_CRYPTS, THE_INNER_SANCTUM (chapters)

However, two_covers.py uses inline art instead of the library. Integration needed.

---

## Tasks

### 1. Art Integration (Priority)
Replace inline art in `src/patternforge/cli/two_covers.py` with library calls:
- `DREAD_CITADEL_BANNER` → use library version or add new
- `LOCK_ART` → use `get_art("LOCK_TIER_N")` based on encounter tier
- Add `from patternforge.adventures.ascii_art import get_art`

### 2. Review & Enhance (If Needed)
Evaluate existing library pieces against SanctuaryRPG/Cogmind standards from your research:
- Are lock tiers visually distinct enough?
- Does CITADEL_LORD read well at terminal size?
- Chapter banners atmospheric enough?

### 3. Scene Art (Optional Enhancement)
Consider adding encounter-type art:
- FLASH encounter icon (quick challenge)
- TOUR encounter icon (guided learning)
- FORK encounter icon (choice moment)
- GAMBIT encounter icon (risk/reward)

---

## Reference

- Your research: `cipher-circle/artifacts/ascii_art_research.md`
- Art library: `src/patternforge/adventures/ascii_art.py`
- Two Covers UI: `src/patternforge/cli/two_covers.py`

---

## Acceptance Criteria

- [x] Two Covers UI uses ascii_art library (no inline art) ✅ 2026-01-25
- [x] Art renders correctly in 80-char terminal ✅ (verified by test_all_art_under_70_chars_wide)
- [x] Visual consistency across all pieces ✅ (all from same library)
- [x] Lock tiers show clear progression ✅ (LOCK_TIER_1 through LOCK_TIER_6)

---

*"ASCII art gives the viewer's imagination a starting point while leaving room for interpretation."*
