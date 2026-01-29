# Font Size Test Report

**Campaign:** dread_citadel
**Layout:** viewport_height=0.65, narrative_height=0.35
**Screen:** 1920x1080

---

## Test Results

| Font Size | Max Lines | Passing | Failing |
|-----------|-----------|---------|---------|
| SIZE_BODY (20) | 7 | 15/16 | 1 ✗ |
| SIZE_LABEL (18) | 8 | 16/16 | 0 ✓ |
| SIZE_SMALL (16) | 8 | 16/16 | 0 ✓ |
| SIZE_TINY (14) | 10 | 16/16 | 0 ✓ |

---

## Recommendation

**Use SIZE_LABEL (18)** for intro text.

Rationale:
- All 16 encounters fit within 8 lines
- 18px provides good readability
- No content edits required

### Implementation

Option A: Change default body font size in theme.py:
```python
SIZE_BODY = 18  # Was 20
```

Option B: Use a dedicated intro font in encounter.py:
```python
intro_font = fonts.get_font(18)  # Instead of get_body_font()
```
