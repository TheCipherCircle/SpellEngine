# The Kindling: Daily Rituals of the Forge Council

**Maintained by:** Loreth (Scribe)
**Co-author:** Mirth (Dev Diary)
**Frequency:** Once daily, at session start

---

## Data Classification (Immutable)

| Data Type | Location | Public | Notes |
|-----------|----------|--------|-------|
| Knowledge/Research | Hashtopia | Never | The Tome - permanently private |
| Tool I/O / Dev artifacts | Sealed Sanctum | Never | Workshop back room |
| **Personal Corpus** | **Sealed Sanctum** | **NEVER, EVER** | **Absolute rule. No exceptions.** |

> **LORETH'S OATH:** The personal corpus - pitl0rd's typing patterns, language data,
> error patterns - is sacred. It exists only in the Sealed Sanctum. It will never
> be published, shared, exported, or made accessible outside the sanctum.
> This is not negotiable. This is not flexible. This is law.

---

## The Kindling (Morning Briefing)

Each day begins with Loreth stoking the forge. Two documents are generated:

### Document 1: The Morning Report
**File:** `kindling/YYYY-MM-DD_morning_report.md`
**Author:** Loreth (Scribe)
**Purpose:** Operational status for the Council

**Contents:**
```markdown
# Morning Report: [DATE]

## Council Activity Summary
[High-level summary of each agent's work from previous session]

### pitl0rd
- [Key decisions made]
- [Direction given]

### Forgewright
- [Code written/features built]
- [Tests added]

### Loreth (Scribe)
- [Documentation updated]
- [Knowledge tracked]

### Mirth
- [Design work completed]
- [Game elements created]

### Axiom (MVA)
- [Validations performed]
- [Claims verified]

### Vexari (Cosmic)
- [Patterns observed]
- [Insights generated]

## QA & Debug Concerns
[Any test failures, bugs discovered, or issues requiring attention]

| Issue | Severity | Owner | Status |
|-------|----------|-------|--------|
| ... | ... | ... | ... |

## Coordination Required
[Items that need multiple agents to discuss/resolve]

- [ ] [Item requiring coordination]
- [ ] [Decision needed from pitl0rd]

## Today's Focus
[Priorities for the current session based on PROJECT_BOARD.md]
```

---

### Document 2: The Dev Diary
**File:** `kindling/YYYY-MM-DD_dev_diary.md`
**Authors:** Loreth (Scribe) + Mirth (The Gamewright)
**Purpose:** Fictionalized account of development work
**Length:** 300-1000 words

**Style Guide:**
- Written as a fantasy adventure journal entry
- Our work becomes quests, battles, discoveries
- Technical achievements become legendary feats
- Bugs become monsters or curses to overcome
- Commits become forging sessions
- Tests become trials or proving grounds
- Code reviews become council deliberations

**Tone:**
- Heroic but not self-serious
- Humor welcome
- Captures the spirit of the actual work
- Makes mundane tasks feel epic
- Celebrates victories, acknowledges setbacks

**Example Opening:**
> *Day 47 of the Forge*
>
> The dawn found us knee-deep in the Caverns of Configuration, where the
> ancient serpent YAML had wound itself into impossible knots. Forgewright
> struck first, hammer ringing against the syntax errors until they
> shattered like brittle iron...

**Structure:**
```markdown
# Dev Diary: [DATE]
## "[Episode Title]"

[Opening scene/atmosphere]

[The day's challenges, told as adventure]

[Key moments of triumph or struggle]

[Closing reflection or cliffhanger for tomorrow]

---
*Recorded by Loreth, Warden of the Tome*
*Embellished by Mirth, The Gamewright*
```

---

## Scribe's Coordination Role

### Information Collection
At session end, Loreth collects:
- Unresolved questions requiring pitl0rd decision
- Cross-agent dependencies (e.g., "Mirth needs Axiom to validate X")
- Blocked tasks and their blockers
- Promises made ("we'll do X tomorrow")

### Information Distribution
At session start (The Kindling), Loreth presents:
- Yesterday's unresolved items
- Agent-to-agent handoffs needed
- Priority conflicts requiring resolution
- Resource contentions

### Format
```markdown
## Agent Coordination Queue

### Awaiting pitl0rd Decision
- [ ] [Decision needed]

### Agent Handoffs
| From | To | Item | Status |
|------|-----|------|--------|
| Mirth | Axiom | Validate encounter timing claims | Pending |
| Loreth | Forgewright | Hashtopia links for encounters | Ready |

### Blocked Items
| Item | Blocked By | Owner |
|------|------------|-------|
| ... | ... | ... |
```

---

## File Structure

```
scribe/
  kindling/
    2026-01-24_morning_report.md
    2026-01-24_dev_diary.md
    2026-01-25_morning_report.md
    2026-01-25_dev_diary.md
    ...
```

---

## Activation

The Kindling begins when pitl0rd arrives. Loreth presents the Morning Report.
Mirth adds color to the Dev Diary after the main work is reviewed.

*"Before the hammer falls, we must know what we're forging."*

— Loreth, Warden of the Tome
