# Cipher Circle Team Practices

## Daily Rhythm

### Campfire Standup (Session Start)

When we begin a work session:

1. **Blockers** - Anyone stuck? What do you need?
2. **Focus** - What's the priority today?
3. **Quick Questions** - Anything that needs a fast decision?

Keep it tight. Save deep discussion for design meetings.

### Progress Report (Session End)

Before we close:

1. **Shipped** - What got done?
2. **Pending** - What's in progress?
3. **Tomorrow** - Who needs what next session?
4. **Blockers** - Anything that will slow us down?

---

## Design Meetings

For major features (like Player Profiles):

### Format

1. **Build plan first** - Document the scope before meeting
2. **Questions queued** - Each team member submits questions
3. **One at a time** - Present each question, get pitl0rd's call
4. **Document immediately** - Update build plan as decisions are made
5. **Summary at end** - All decisions in one table

### Question Format

```
**Question N of M**

*[Agent name] asks:*

[Question text]

Options:
- **A)** [Option A description]
- **B)** [Option B description]
- **C)** [Option C description]
```

### After Meeting

- Build plan marked APPROVED
- All decisions documented
- Ready for implementation

---

## Collaboration Protocol

From Literary Release Materials (TODO.md):

| Review Type | Agent | Responsibility |
|-------------|-------|----------------|
| **Factual/Lore** | Loreth | Accuracy, consistency with established lore |
| **Engagement** | Mirth | Pacing, readability, "is this fun to read?" |
| **Visuals/Art** | Fraz | Beautification, ASCII art, layout |
| **Data Viz** | Prism | Charts, diagrams, data accuracy |
| **Technical** | Forge | Code claims, architecture accuracy |
| **Security** | Vex | Vulnerabilities, edge cases, tampering |
| **Testing** | Anvil | Coverage, test strategy, quality gates |
| **Edge Cases** | Jinx | Adversarial review, what could go wrong |

**Workflow:** Write → Review chain → pitl0rd approval → Ship

---

## Code Quality Standards

- Explore codebase before proposing changes
- Follow existing patterns
- Tests for new functionality
- Platform testing (macOS, Windows, Linux)
- Documentation updated

---

## Session Notes

Keep notes in `cipher-circle/session-notes/` for continuity across context windows.

---

*Established 2026-01-25*
