# PatternForge Ecosystem - Agent Onboarding

> *Maintained by Loreth the Scribe. All new agents receive this document.*

## Repositories

| Repo | URL | Purpose |
|------|-----|---------|
| **PatternForge** | `github.com/pitl0rd/PatternForge` | Main platform - CLI, engines, game system |
| **GemOfSeeing** | `github.com/pitl0rd/GemOfSeeing` | Data analytics & visualization framework (new) |

Local paths:
- `/Users/petermckernan/Projects/PatternForge`
- `/Users/petermckernan/Projects/GemOfSeeing`

---

## What PatternForge Does

PatternForge is a modular platform for structural password analysis and candidate generation. It is NOT a password cracker - it generates input artifacts for tools like Hashcat.

**Core Flow:**
```
Ingest corpus → SCARAB (analyze) → ModelBundle → EntropySmith (generate) → Artifacts
```

**3-Tier Architecture:**
- **Tier 1 (Core):** SCARAB + EntropySmith engines - pure computation, no I/O
- **Tier 2 (Workflow):** CLI, pipelines, storage, exporters
- **Tier 3 (Game):** PTHAdventures - educational campaigns teaching hash cracking

See `ARCHITECTURE.md` and `CLAUDE.md` in the PatternForge repo for full details.

---

## What GemOfSeeing Does

Analytics and visualization framework that takes ModelBundle data and presents it to different research audiences through "lenses" (audience filters) and "visions" (visualization types).

See `DESIGN.md` in the GemOfSeeing repo for the full design spec.

---

## Current Priorities

1. **Game is the focus** - PTHAdventures campaigns are the current priority
2. **Dread Citadel campaign** - Complete beginner campaign (just shipped)
3. **GemOfSeeing scaffold** - Ready for implementation
4. **Research efficiency** - Keep iteration fast, don't over-engineer

---

## The Forge Council (Agent Personas)

These are in-universe personas used for specialized tasks:

| Agent | Role | Domain |
|-------|------|--------|
| **Axiom** | Math Validator | Statistical validation, confidence scoring |
| **Vexari** | Pattern Observer | Correlation, insights, roadmap proposals |
| **Loreth (Scribe)** | Knowledge Steward | Documentation, data qualification, knowledge base |
| **Mirth** | Gamewright | Encounter design, difficulty tuning, quest hooks |
| **Anvil** | Validator | QA, testing, platform certification, edge cases |
| **Fraz** | Pigment Alchemist | ASCII art, visual polish, terminal aesthetics |
| **Jinx** | Neural Architect | NeuralSmith engine, GAN/GPT/LSTM, binary building |

When working on game content, channel Mirth. When documenting, channel Loreth/Scribe.

---

## Key Files to Read First

**PatternForge:**
- `CLAUDE.md` - Project overview and CLI commands
- `ARCHITECTURE.md` - 3-tier system and fork strategy
- `src/patternforge/campaigns/dread_citadel.yaml` - Example campaign structure
- `src/patternforge/adventures/models.py` - Game data models

**GemOfSeeing:**
- `DESIGN.md` - Full design spec and API examples

---

## Working Style

- **CLI-first** - Everything should be scriptable
- **No over-engineering** - Minimum complexity for current needs
- **Profile before optimizing** - Don't assume bottlenecks
- **Gruvbox theme** - CLI uses Gruvbox color palette
- **Cross-platform** - Unicode symbols have ASCII fallbacks

---

## If You Encounter Another Agent

1. Check `ARCHITECTURE.md` for tier boundaries - don't cross them unnecessarily
2. Tier 1 (engines) has no I/O - pass data as arguments
3. Campaigns go in `src/patternforge/campaigns/`
4. Tests mirror source structure in `tests/unit/`
5. Commit messages use conventional commits: `feat:`, `fix:`, `docs:`
6. Co-author line: `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`

---

## Quick Commands

```bash
# Run tests
python3 -m pytest tests/unit/ -v

# List adventures
python3 -m patternforge adventure list

# Start a campaign
python3 -m patternforge adventure start dread_citadel

# Check imports work
python3 -c "from patternforge.engines import SCARABAnalyzer, EntropySmithGenerator"
```

---

## Changelog

| Date | Update |
|------|--------|
| 2025-01-24 | Initial creation - PatternForge + GemOfSeeing |

---

*Welcome to the Forge. Build well.*
