# Content Quality Scorecard

**Purpose:** Evaluate content before publication to ensure high quality and audience fit.

---

## The EIE Triangle

All content balances three qualities:

```
                    EDUCATIONAL
                         ▲
                        /|\
                       / | \
                      /  |  \
                     /   |   \
                    /    |    \
                   /     |     \
                  /      |      \
                 /       |       \
                /________|________\
         INFORMATIVE ◄───────► ENTERTAINING
```

**Different content types target different balances:**

| Content Type | Educational | Informative | Entertaining | Notes |
|--------------|:-----------:|:-----------:|:------------:|-------|
| **White Papers** | ●●○ | ●●● | ●○○ | Heavy on information, some teaching |
| **Scholar's Chronicles** | ●○○ | ●●○ | ●●● | Entertainment-forward, personality-driven |
| **Why We Built This** | ●●○ | ●●○ | ●●○ | Balanced - story that teaches |
| **Making Of / Team Story** | ●○○ | ●●○ | ●●● | Character-driven, fun |
| **Quick Start Guide** | ●●● | ●●○ | ●○○ | Teaching-focused, practical |
| **README** | ●●○ | ●●● | ●○○ | Reference material |
| **Social Media Posts** | ●○○ | ●○○ | ●●● | Hook and engage |
| **Blog Articles** | ●●○ | ●●○ | ●●○ | Balanced mix |

### Humor Scale

**Humor scales directly with Entertainment level.** This is a hard rule.

| Entertainment Level | Humor Allowed | Examples |
|:-------------------:|---------------|----------|
| ●○○ | **None** | White papers, research docs, scientific publications, technical specs |
| ●●○ | **Light** | Occasional wit, clever phrasing - but never jokes |
| ●●● | **Full** | Personality, jokes, puns, character voice, playfulness |

**Zero humor content types:**
- White Papers
- Research Publications
- Technical Documentation
- API References
- Scientific Analysis
- Security Advisories

**Full humor content types:**
- Scholar's Chronicles (interviews)
- Social Media Posts
- Making Of / Team Stories
- Character-driven narratives

**Light humor content types:**
- Blog Articles
- README (can have personality, not jokes)
- Why We Built This (storytelling warmth, not comedy)

---

## Scoring Dimensions

Rate each dimension: 🟢 Good | 🟡 Needs Work | 🔴 Problem

### 1. Readability
*Can the target audience easily follow this?*

| Score | Criteria |
|-------|----------|
| 🟢 | Flows naturally, appropriate sentence length, clear structure |
| 🟡 | Some dense sections, occasional jargon without explanation |
| 🔴 | Confusing structure, walls of text, unexplained terminology |

### 2. Tone
*Does it feel like it came from the Cipher Circle?*

| Score | Criteria |
|-------|----------|
| 🟢 | Consistent voice, matches content type, feels authentic |
| 🟡 | Tone wavers, some sections feel off-brand |
| 🔴 | Wrong tone entirely, corporate-speak, or inconsistent throughout |

### 3. Style
*Is the writing quality high?*

| Score | Criteria |
|-------|----------|
| 🟢 | Engaging prose, good rhythm, memorable phrases |
| 🟡 | Functional but flat, could use polish |
| 🔴 | Awkward phrasing, repetitive, boring |

### 4. Density
*Is the content appropriately packed?*

| Score | Criteria |
|-------|----------|
| 🟢 | Right amount of content for format, good pacing |
| 🟡 | Too dense or too sparse in places |
| 🔴 | Overwhelming or feels padded/thin |

### 5. EIE Balance
*Does it hit the target balance for its content type?*

| Score | Criteria |
|-------|----------|
| 🟢 | Matches intended balance, serves purpose |
| 🟡 | Slightly off-target, could adjust emphasis |
| 🔴 | Wrong balance entirely (e.g., boring white paper that should inform) |

---

## Audience Assessment

After scoring, answer these questions:

### Who is this for?
- [ ] Security professionals (practitioners)
- [ ] Security students/learners
- [ ] Developers interested in security
- [ ] AI/ML enthusiasts
- [ ] Game design enthusiasts
- [ ] General tech audience
- [ ] PatternForge users (existing)
- [ ] Potential PatternForge users (new)

### Who will connect with this?
*Be specific. Not "everyone" - who will actually share this?*

```
Primary audience: _______________
Secondary audience: _______________
This will resonate because: _______________
This might NOT resonate with _______________ because _______________
```

### Distribution fit
- [ ] Twitter/X (short, punchy, shareable)
- [ ] LinkedIn (professional, insightful)
- [ ] Blog/Medium (long-form, searchable)
- [ ] README/Docs (reference, practical)
- [ ] Conference talk (narrative, visual)
- [ ] Press/media (newsworthy, quotable)

---

## Review Template

```markdown
# Content Review: [Title]

**Content Type:** [White Paper / Interview / Blog / etc.]
**Target EIE:** Educational ●●○ | Informative ●●● | Entertaining ●○○
**Reviewer:** [Agent name]
**Date:** YYYY-MM-DD

## Scores

| Dimension | Score | Comments |
|-----------|-------|----------|
| Readability | 🟢/🟡/🔴 | |
| Tone | 🟢/🟡/🔴 | |
| Style | 🟢/🟡/🔴 | |
| Density | 🟢/🟡/🔴 | |
| EIE Balance | 🟢/🟡/🔴 | |

## Audience Assessment

**Primary audience:**
**Secondary audience:**
**Will resonate because:**
**Risk of not connecting with:**

## Specific Feedback

### What's working well
-

### What needs improvement
-

### Recommended changes
1.
2.
3.

## Verdict

- [ ] 🟢 Ready to publish
- [ ] 🟡 Publish after minor revisions
- [ ] 🔴 Needs significant rework

**Overall notes:**
```

---

## Review Workflow

```
┌─────────────┐
│   DRAFT     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────────────────────────┐
│   LORETH    │────►│ Factual accuracy, lore check    │
│  (Review 1) │     │ Fill out scorecard              │
└──────┬──────┘     └─────────────────────────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────────────────────────┐
│   MIRTH     │────►│ Engagement, pacing, fun factor  │
│  (Review 2) │     │ EIE balance assessment          │
└──────┬──────┘     └─────────────────────────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────────────────────────┐
│   FRAZ      │────►│ Visual polish, art integration  │
│  (Art Pass) │     │ Layout and presentation         │
└──────┬──────┘     └─────────────────────────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────────────────────────┐
│   PRISM     │────►│ Data viz review (if applicable) │
│  (Data Viz) │     │ Chart accuracy, visual clarity  │
└──────┬──────┘     └─────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  PUBLISH    │
└─────────────┘
```

---

## Content Type Profiles

### White Papers
**Target:** Informative-heavy, some educational value
**Tone:** Professional, authoritative, accessible but serious
**Humor:** ⛔ **NONE** - No jokes, puns, or humor of any kind
**Audience:** Security professionals, researchers, potential adopters
**EIE:** Educational ●●○ | Informative ●●● | Entertaining ●○○

**Watch for:**
- Too much jargon without explanation
- Missing the "so what?" - why does this matter?
- Dry academic tone (be clear and direct, not stuffy)
- Any humor creeping in - remove it

**Engagement without humor:**
- Compelling narrative structure
- Clear value propositions
- Well-organized information hierarchy
- Strong opening and closing

### Scholar's Chronicles (Interviews)
**Target:** Entertainment-forward, personality-driven
**Tone:** Conversational, fun, character voices shine through
**Humor:** ✅ **FULL** - Jokes, puns, wit, playfulness all welcome
**Audience:** Community, fans, people who want to know the team
**EIE:** Educational ●○○ | Informative ●●○ | Entertaining ●●●

**Watch for:**
- Being too serious or formal
- Characters sounding the same (each agent has a voice!)
- Missing opportunities for humor or charm
- Forgetting to include actual interesting information
- Humor that punches down or excludes

### Technical Documentation
**Target:** Educational, practical, reference
**Tone:** Clear, helpful, efficient
**Humor:** ⛔ **NONE** - Strictly functional
**Audience:** Users trying to accomplish something
**EIE:** Educational ●●● | Informative ●●○ | Entertaining ●○○

**Watch for:**
- Assuming too much knowledge
- Missing examples
- Walls of text without structure
- Forgetting the user is trying to DO something

---

## Quality Gates

### Minimum for Publication
- No 🔴 scores
- Maximum one 🟡 score (and it must be minor)
- Audience assessment completed
- At least two reviewers signed off

### Excellence Standard
- All 🟢 scores
- Clear audience fit
- Memorable/shareable elements identified
- Team consensus on quality

---

*"We don't ship content. We ship experiences."* — Mirth
