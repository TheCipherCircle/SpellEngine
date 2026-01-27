# Lessons Learned

*What the Cipher Circle has discovered*

---

## Phase 1: PatternForge Foundation

### What Worked

1. **Separate analysis from generation**
   - SCARAB does one thing well (structural analysis)
   - EntropySmith does one thing well (candidate synthesis)
   - Clean boundaries, testable components

2. **Test as you build**
   - 609 tests caught real issues
   - Engine tests revealed API misunderstandings
   - Smoke tests verify the full pipeline

3. **Don't over-engineer early**
   - NetherImps (QA sub-agents) were scope creep
   - "What do we do RIGHT NOW" keeps focus
   - Build CI/CD when users arrive, not before

4. **Designed data must work quickly**
   - Teaching exercises need instant feedback
   - Unless the lesson IS about time/iteration

### What We'd Do Differently

1. **Write engine tests first**
   - Discovered API assumptions were wrong
   - Would have caught ConstraintParams interface earlier

2. **Check CLI interface before writing smoke tests**
   - `list --corpora` not `list corpora`
   - Read the help output first

---

## Patterns Discovered

### pitl0rd Preferences
- Prefers direct answers over hedging
- Values "reel me in" when planning too far ahead
- Likes thematic naming (Sealed Sanctum, Cipher Circle)
- Appreciates when we don't over-complicate

### Session Rhythm
- Morning: The Kindling (standup, plan)
- Work: Focus blocks with clear goals
- End: Commit, summarize, set next steps

---

*Last Updated: 2026-01-24*
