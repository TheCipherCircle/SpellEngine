# PTHAdventures Encounter Framework
## Visual Architecture & Game Paths

---

## Skeleton Taxonomy (Expanded)

```
ENCOUNTER SKELETONS
═══════════════════════════════════════════════════════════════════════════════

                            ┌─────────────────┐
                            │   ALL SKELETONS │
                            └────────┬────────┘
                                     │
        ┌────────────────┬───────────┼───────────┬────────────────┐
        ▼                ▼           ▼           ▼                ▼
   ┌─────────┐     ┌──────────┐ ┌─────────┐ ┌─────────┐    ┌───────────┐
   │ INSTANT │     │ GUIDED   │ │ OPEN    │ │ TIMED   │    │ BRANCHING │
   │ (< 10s) │     │ (Linear) │ │ (Free)  │ │ (Clock) │    │ (Choice)  │
   └────┬────┘     └────┬─────┘ └────┬────┘ └────┬────┘    └─────┬─────┘
        │               │            │           │               │
   ┌────┴────┐     ┌────┴────┐  ┌────┴────┐ ┌────┴────┐    ┌─────┴─────┐
   │         │     │         │  │         │ │         │    │           │
   ▼         ▼     ▼         ▼  ▼         ▼ ▼         ▼    ▼           ▼
┌──────┐ ┌──────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌─────┐ ┌─────┐
│FLASH │ │LOOKUP│ │TOUR│ │WALK│ │HUNT│ │CRAFT│ │RACE│ │SIEGE│ │FORK │ │GAMBIT│
└──────┘ └──────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └─────┘ └─────┘ └──────┘
```

---

## The 15 Skeleton Types

### INSTANT Category (Reflex & Recognition)

```
┌─────────────────────────────────────────────────────────────────┐
│  FLASH                                                          │
│  ═══════                                                        │
│  Pattern: See → React → Done                                    │
│  Feel: Quick reflex, pattern recognition                        │
│  Time: < 5 seconds                                              │
│                                                                 │
│  ┌────────┐    ┌────────┐    ┌────────┐                        │
│  │ PROMPT │───▶│ ANSWER │───▶│ RESULT │                        │
│  └────────┘    └────────┘    └────────┘                        │
│                                                                 │
│  Examples:                                                      │
│  - "What type is this hash?" (see → identify → done)           │
│  - "Which command lists corpora?" (recall → answer → done)     │
│  - "Is this salted?" (observe → decide → done)                 │
│                                                                 │
│  Tiers: 0-2  │  Data: Single artifact  │  Validation: Instant  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LOOKUP                                                         │
│  ════════                                                       │
│  Pattern: Question → Search → Find → Report                     │
│  Feel: Research, discovery, reading comprehension               │
│  Time: 30 seconds - 2 minutes                                   │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ QUESTION │───▶│  SEARCH  │───▶│   FIND   │───▶│  ANSWER  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                   Hashtopia       The page        Quote or      │
│                   or --help       with answer     summarize     │
│                                                                 │
│  Examples:                                                      │
│  - "What is the default iteration count for bcrypt?"           │
│  - "Find the mask syntax for lowercase letters"                │
│  - "What does SCARAB stand for?"                               │
│                                                                 │
│  Tiers: 0-1  │  Data: None (docs)  │  Validation: Text match   │
└─────────────────────────────────────────────────────────────────┘
```

### GUIDED Category (Structured Learning)

```
┌─────────────────────────────────────────────────────────────────┐
│  TOUR                                                           │
│  ══════                                                         │
│  Pattern: Guide speaks → Player follows → Checkpoints           │
│  Feel: Museum tour, narrated walkthrough, safe exploration      │
│  Time: 2-5 minutes                                              │
│                                                                 │
│  ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐    │
│  │ INTRO │──▶│ STOP 1│──▶│ STOP 2│──▶│ STOP 3│──▶│ FINALE│    │
│  └───────┘   └───┬───┘   └───┬───┘   └───┬───┘   └───────┘    │
│                  │           │           │                      │
│               [check]     [check]     [check]                   │
│               "Got it?"   "See that?" "Ready?"                  │
│                                                                 │
│  Examples:                                                      │
│  - Tour of PatternForge CLI commands                           │
│  - Walkthrough of a ModelBundle structure                      │
│  - Guided exploration of Hashtopia sections                    │
│                                                                 │
│  Tiers: 1-2  │  Data: None  │  Validation: Checkpoint confirms │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  WALKTHROUGH                                                    │
│  ═══════════                                                    │
│  Pattern: Step-by-step with player executing each step          │
│  Feel: Cooking recipe, assembly instructions                    │
│  Time: 5-10 minutes                                             │
│                                                                 │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐            │
│  │ STEP 1 │──▶│ STEP 2 │──▶│ STEP 3 │──▶│ COMPLETE│           │
│  │ Do X   │   │ Do Y   │   │ Do Z   │   │ Victory │           │
│  └───┬────┘   └───┬────┘   └───┬────┘   └─────────┘           │
│      │            │            │                                │
│   [execute]    [execute]    [execute]                          │
│   [validate]   [validate]   [validate]                         │
│                                                                 │
│  Examples:                                                      │
│  - Ingest → Analyze → Forge → Export (full workflow)          │
│  - Create wordlist → Apply rules → Generate candidates         │
│  - Set up environment → Configure → Run first crack            │
│                                                                 │
│  Tiers: 3-4  │  Data: Practice files  │  Validation: Per-step  │
└─────────────────────────────────────────────────────────────────┘
```

### OPEN Category (Player Agency)

```
┌─────────────────────────────────────────────────────────────────┐
│  HUNT                                                           │
│  ══════                                                         │
│  Pattern: Given target, find it however you want                │
│  Feel: Scavenger hunt, detective work, exploration              │
│  Time: Variable (player-driven)                                 │
│                                                                 │
│           ┌──────────┐                                         │
│           │  TARGET  │                                         │
│           │ "Find X" │                                         │
│           └────┬─────┘                                         │
│                │                                                │
│       ┌────────┼────────┐                                      │
│       ▼        ▼        ▼                                      │
│    ┌─────┐  ┌─────┐  ┌─────┐                                  │
│    │Path │  │Path │  │Path │   (Any path to victory)          │
│    │  A  │  │  B  │  │  C  │                                  │
│    └──┬──┘  └──┬──┘  └──┬──┘                                  │
│       └────────┼────────┘                                      │
│                ▼                                                │
│           ┌─────────┐                                          │
│           │ VICTORY │                                          │
│           └─────────┘                                          │
│                                                                 │
│  Examples:                                                      │
│  - "Find a hash in this dump that's MD5" (any valid MD5)      │
│  - "Locate the config file" (grep, find, ls - your choice)    │
│  - "Get the password" (any working attack method)             │
│                                                                 │
│  Tiers: 4-5  │  Data: Rich environment  │  Validation: Result  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CRAFT                                                          │
│  ═══════                                                        │
│  Pattern: Given materials, build something that works           │
│  Feel: Crafting table, workshop, creative problem-solving       │
│  Time: 5-15 minutes                                             │
│                                                                 │
│    ┌────────────┐                                              │
│    │ MATERIALS  │  (What you have)                             │
│    │ ────────── │                                              │
│    │ • wordlist │                                              │
│    │ • rules    │                                              │
│    │ • masks    │                                              │
│    └─────┬──────┘                                              │
│          │                                                      │
│          ▼                                                      │
│    ┌───────────┐                                               │
│    │  COMBINE  │  (Player decides how)                         │
│    └─────┬─────┘                                               │
│          │                                                      │
│          ▼                                                      │
│    ┌───────────┐                                               │
│    │  PRODUCT  │  (Does it work?)                              │
│    └───────────┘                                               │
│                                                                 │
│  Examples:                                                      │
│  - Build an attack that cracks this hash                       │
│  - Construct a mask for 8-char passwords starting with caps   │
│  - Create a rule that appends years                            │
│                                                                 │
│  Tiers: 4-6  │  Data: Components + target  │  Validation: Works│
└─────────────────────────────────────────────────────────────────┘
```

### TIMED Category (Pressure & Pacing)

```
┌─────────────────────────────────────────────────────────────────┐
│  RACE                                                           │
│  ══════                                                         │
│  Pattern: Complete before time runs out                         │
│  Feel: Speed run, time attack, urgency                          │
│  Time: Fixed limit (30s, 60s, 120s)                            │
│                                                                 │
│    ════════════════════════════════════════                    │
│    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓▓▓▓▓▓▓▓  TIME BAR           │
│    ════════════════════════════════════════                    │
│                                                                 │
│         ┌──────────┐                                           │
│         │   TASK   │                                           │
│         └────┬─────┘                                           │
│              │                                                  │
│         ┌────┴────┐                                            │
│         ▼         ▼                                            │
│    ┌─────────┐ ┌─────────┐                                     │
│    │ IN TIME │ │ TOO SLOW│                                     │
│    │ +Bonus  │ │ No bonus│                                     │
│    └─────────┘ └─────────┘                                     │
│                                                                 │
│  Examples:                                                      │
│  - Identify 5 hash types in 60 seconds                         │
│  - Build and execute attack before "alarm triggers"           │
│  - Fix the broken command before output buffer fills          │
│                                                                 │
│  Tiers: 2-5  │  Data: Quick-crack  │  Validation: Time + Result│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SIEGE                                                          │
│  ═══════                                                        │
│  Pattern: Progressive attack, watch it unfold, learn pattern    │
│  Feel: Tower defense, watching progress, patience               │
│  Time: INTENTIONALLY LONG (this IS the lesson)                 │
│                                                                 │
│    Progress: ████████████░░░░░░░░░░░░░░░░░░░░  35%             │
│                                                                 │
│    ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐       │
│    │Wave 1│──▶│Wave 2│──▶│Wave 3│──▶│Wave 4│──▶│ DONE │       │
│    │ Easy │   │Medium│   │ Hard │   │ Boss │   │      │       │
│    │ 10%  │   │ 25%  │   │ 15%  │   │ 50%  │   │ 100% │       │
│    └──────┘   └──────┘   └──────┘   └──────┘   └──────┘       │
│       ▲          ▲          ▲          ▲                       │
│    [observe]  [observe]  [observe]  [observe]                  │
│    "Notice    "Why did   "What's    "Lesson                   │
│     this?"    it slow?"  left?"     learned"                  │
│                                                                 │
│  Examples:                                                      │
│  - Watch dictionary attack exhaust common passwords first     │
│  - Observe mask attack find patterns progressively            │
│  - See failure clusters emerge in real-time                   │
│                                                                 │
│  Tiers: 4-6  │  Data: Progressive corpus  │  Validation: Obs  │
│  ⚠️  CLEARLY LABELED: "This takes time - that's the point"     │
└─────────────────────────────────────────────────────────────────┘
```

### BRANCHING Category (Meaningful Choices)

```
┌─────────────────────────────────────────────────────────────────┐
│  FORK                                                           │
│  ══════                                                         │
│  Pattern: Choose path A or B, each teaches different lesson     │
│  Feel: Choose your own adventure, meaningful decision           │
│  Time: Varies by path                                           │
│                                                                 │
│              ┌─────────┐                                       │
│              │ CHOICE  │                                       │
│              │ POINT   │                                       │
│              └────┬────┘                                       │
│                   │                                             │
│         ┌─────────┴─────────┐                                  │
│         ▼                   ▼                                  │
│    ┌─────────┐         ┌─────────┐                            │
│    │ PATH A  │         │ PATH B  │                            │
│    │ "Brute  │         │ "Smart  │                            │
│    │  Force" │         │  Recon" │                            │
│    └────┬────┘         └────┬────┘                            │
│         │                   │                                  │
│    ┌────┴────┐         ┌────┴────┐                            │
│    │ LESSON  │         │ LESSON  │                            │
│    │ "Costs  │         │ "Intel  │                            │
│    │  scale" │         │  saves" │                            │
│    └────┬────┘         └────┬────┘                            │
│         │                   │                                  │
│         └─────────┬─────────┘                                  │
│                   ▼                                             │
│              ┌─────────┐                                       │
│              │ REUNITE │  Both paths valid, different wisdom   │
│              └─────────┘                                       │
│                                                                 │
│  Examples:                                                      │
│  - "Quick dictionary attack" vs "Profile the target first"    │
│  - "Use wizard" vs "Go manual"                                 │
│  - "Crack one thoroughly" vs "Spray many quickly"             │
│                                                                 │
│  Tiers: 3-5  │  Data: Both paths work  │  Validation: Either  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  GAMBIT                                                         │
│  ════════                                                       │
│  Pattern: Risk/reward choice with consequences                  │
│  Feel: Gambling, calculated risk, strategy                      │
│  Time: Quick decision, variable outcome                         │
│                                                                 │
│              ┌───────────┐                                     │
│              │   GAMBIT  │                                     │
│              │  OFFERED  │                                     │
│              └─────┬─────┘                                     │
│                    │                                            │
│         ┌──────────┴──────────┐                                │
│         ▼                     ▼                                │
│    ┌──────────┐         ┌──────────┐                          │
│    │ SAFE BET │         │ HIGH RISK│                          │
│    │ ──────── │         │ ──────── │                          │
│    │ Low cost │         │ High cost│                          │
│    │ Low gain │         │ High gain│                          │
│    │ 100% win │         │ 50% win  │                          │
│    └────┬─────┘         └────┬─────┘                          │
│         │                    │                                 │
│         │               ┌────┴────┐                           │
│         │               ▼         ▼                           │
│         │          ┌───────┐ ┌───────┐                        │
│         │          │SUCCESS│ │FAILURE│                        │
│         │          │ Jackpot│ │Setback│                       │
│         │          └───────┘ └───────┘                        │
│         │               │         │                            │
│         └───────────────┴────┬────┘                           │
│                              ▼                                 │
│                        ┌──────────┐                           │
│                        │  LESSON  │                           │
│                        │ in risk  │                           │
│                        │ analysis │                           │
│                        └──────────┘                           │
│                                                                 │
│  Examples:                                                      │
│  - "Try common passwords only (safe)" vs "Full attack (risky)"│
│  - "Spend hints now" vs "Save for harder challenge"           │
│  - "Skip hash (0 pts)" vs "Attempt (fail = -10, win = +50)"  │
│                                                                 │
│  Tiers: 4-6  │  Data: Tuned difficulty  │  Validation: Outcome │
└─────────────────────────────────────────────────────────────────┘
```

### SPECIAL Category (Unique Mechanics)

```
┌─────────────────────────────────────────────────────────────────┐
│  PUZZLE BOX                                                     │
│  ══════════                                                     │
│  Pattern: Multi-step puzzle, unlock sequence                    │
│  Feel: Escape room, combination lock, layered mystery           │
│  Time: 10-20 minutes                                            │
│                                                                 │
│         ┌─────┐                                                │
│         │ 🔒  │  Locked                                        │
│         └──┬──┘                                                │
│            │                                                    │
│    ┌───────┼───────┐                                          │
│    ▼       ▼       ▼                                          │
│  ┌───┐   ┌───┐   ┌───┐                                        │
│  │ A │   │ B │   │ C │  Three clues to find                   │
│  └─┬─┘   └─┬─┘   └─┬─┘                                        │
│    │       │       │                                           │
│    ▼       ▼       ▼                                           │
│  [key1] [key2] [key3]   Each unlocks part                     │
│    │       │       │                                           │
│    └───────┼───────┘                                          │
│            ▼                                                    │
│         ┌─────┐                                                │
│         │ 🔓  │  Unlocked!                                     │
│         └─────┘                                                │
│                                                                 │
│  Examples:                                                      │
│  - Find hash type → Find salt location → Decode salt → Crack │
│  - Parse log → Extract pattern → Build mask → Execute        │
│  - Three partial passwords that combine into attack vector    │
│                                                                 │
│  Tiers: 5-6  │  Data: Multi-part  │  Validation: Final unlock  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DUEL                                                           │
│  ══════                                                         │
│  Pattern: Compare two approaches, argue for better one          │
│  Feel: Debate, critical thinking, trade-off analysis            │
│  Time: 5-10 minutes                                             │
│                                                                 │
│        ┌───────────┐                                           │
│        │ SCENARIO  │                                           │
│        └─────┬─────┘                                           │
│              │                                                  │
│    ┌─────────┴─────────┐                                      │
│    ▼                   ▼                                      │
│  ┌──────────┐     ┌──────────┐                                │
│  │APPROACH A│ vs  │APPROACH B│                                │
│  │ ──────── │     │ ──────── │                                │
│  │ Pros:    │     │ Pros:    │                                │
│  │ • Fast   │     │ • Thorough│                               │
│  │ Cons:    │     │ Cons:    │                                │
│  │ • Misses │     │ • Slow   │                                │
│  └──────────┘     └──────────┘                                │
│        │               │                                       │
│        └───────┬───────┘                                      │
│                ▼                                               │
│        ┌─────────────┐                                        │
│        │PLAYER CHOICE│  "Which and why?"                      │
│        └──────┬──────┘                                        │
│               ▼                                                │
│        ┌─────────────┐                                        │
│        │ EVALUATION  │  Both valid; reasoning matters         │
│        └─────────────┘                                        │
│                                                                 │
│  Examples:                                                      │
│  - Dictionary vs Mask attack for this target                  │
│  - Parallel vs Sequential attack strategy                     │
│  - Crack now vs Gather more intel                             │
│                                                                 │
│  Tiers: 3-5  │  Data: Scenario desc  │  Validation: Reasoning  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  REPAIR                                                         │
│  ════════                                                       │
│  Pattern: Fix broken command/config/output                      │
│  Feel: Debugging, troubleshooting, error analysis               │
│  Time: 2-10 minutes                                             │
│                                                                 │
│    ┌─────────────────────────────────────┐                     │
│    │  BROKEN THING                        │                     │
│    │  ════════════                        │                     │
│    │  $ patternforg analyz --engine scrab │ ← errors           │
│    │  Error: command not found            │                     │
│    └───────────────────┬─────────────────┘                     │
│                        │                                        │
│                        ▼                                        │
│    ┌─────────────────────────────────────┐                     │
│    │  PLAYER FIXES                        │                     │
│    │  ════════════                        │                     │
│    │  $ patternforge analyze --engine scarab │                 │
│    └───────────────────┬─────────────────┘                     │
│                        │                                        │
│                        ▼                                        │
│    ┌─────────────────────────────────────┐                     │
│    │  ✓ WORKS                            │                     │
│    └─────────────────────────────────────┘                     │
│                                                                 │
│  Examples:                                                      │
│  - Fix typo in command                                         │
│  - Correct malformed mask syntax                               │
│  - Debug why export failed                                     │
│  - Identify missing dependency                                 │
│                                                                 │
│  Tiers: 2-5  │  Data: Broken samples  │  Validation: Runs     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skeleton Summary Table

```
┌────────────────┬──────────────┬────────┬─────────────────────────────────┐
│ SKELETON       │ CATEGORY     │ TIERS  │ FEEL                            │
├────────────────┼──────────────┼────────┼─────────────────────────────────┤
│ FLASH          │ Instant      │ 0-2    │ Quick recognition               │
│ LOOKUP         │ Instant      │ 0-1    │ Research, finding               │
│ TOUR           │ Guided       │ 1-2    │ Narrated exploration            │
│ WALKTHROUGH    │ Guided       │ 3-4    │ Step-by-step execution          │
│ HUNT           │ Open         │ 4-5    │ Scavenger hunt, freedom         │
│ CRAFT          │ Open         │ 4-6    │ Creative building               │
│ RACE           │ Timed        │ 2-5    │ Speed pressure                  │
│ SIEGE          │ Timed        │ 4-6    │ Patient observation             │
│ FORK           │ Branching    │ 3-5    │ Meaningful choice               │
│ GAMBIT         │ Branching    │ 4-6    │ Risk/reward                     │
│ PUZZLE BOX     │ Special      │ 5-6    │ Layered mystery                 │
│ DUEL           │ Special      │ 3-5    │ Critical comparison             │
│ REPAIR         │ Special      │ 2-5    │ Debugging                       │
│ PIPELINE       │ Shell        │ 5-6    │ Command chaining                │
│ SCRIPT         │ Shell        │ 6      │ Automation                      │
└────────────────┴──────────────┴────────┴─────────────────────────────────┘
```

---

## Game Path Architecture

### Tale Structure (Branching Tree)

```
                        ══════════════════════════════════
                              TALE 1: THE WANDERER'S ARRIVAL
                        ══════════════════════════════════
                                         │
                                         ▼
                               ┌───────────────────┐
                               │   CHAPTER 1       │
                               │   "First Steps"   │
                               │   (Mandatory)     │
                               └─────────┬─────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
              ┌──────────┐        ┌──────────┐        ┌──────────┐
              │ E1: TOUR │        │ E2: FLASH│        │ E3:LOOKUP│
              │ "The     │        │ "Quick   │        │ "The     │
              │  Blade"  │        │  Test"   │        │  Tome"   │
              └────┬─────┘        └────┬─────┘        └────┬─────┘
                   │                   │                   │
                   └───────────────────┴───────────────────┘
                                       │
                                       ▼
                               ┌───────────────────┐
                               │   CHAPTER 2       │
                               │  "Choose Path"    │
                               │  (Player Choice)  │
                               └─────────┬─────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
                   ┌─────────────┐               ┌─────────────┐
                   │  PATH A     │               │  PATH B     │
                   │ "The Forge" │               │ "The Study" │
                   │ (Hands-on)  │               │ (Theory)    │
                   └──────┬──────┘               └──────┬──────┘
                          │                             │
              ┌───────────┴───────────┐     ┌───────────┴───────────┐
              ▼           ▼           ▼     ▼           ▼           ▼
         ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
         │WALK-   │ │ CRAFT  │ │ RACE   │ │ LOOKUP │ │ DUEL   │ │ TOUR   │
         │THROUGH │ │        │ │        │ │ x3     │ │        │ │        │
         └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
             │          │          │          │          │          │
             └──────────┴──────────┴──────────┴──────────┴──────────┘
                                       │
                                       ▼
                               ┌───────────────────┐
                               │   CHAPTER 3       │
                               │  "Convergence"    │
                               │  (Paths Reunite)  │
                               └─────────┬─────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
                   ┌─────────────┐               ┌─────────────┐
                   │ E: HUNT     │               │ E: GAMBIT   │
                   │ "Find the   │               │ "Risk the   │
                   │  Hash"      │               │  Attack?"   │
                   └──────┬──────┘               └──────┬──────┘
                          │                             │
                          └──────────────┬──────────────┘
                                         ▼
                               ┌───────────────────┐
                               │   CHAPTER 4       │
                               │   "The Test"      │
                               │   (Gate Check)    │
                               └─────────┬─────────┘
                                         │
                                         ▼
                               ┌───────────────────┐
                               │   GATE ENCOUNTER  │
                               │   (PUZZLE BOX)    │
                               │   Must Pass       │
                               └─────────┬─────────┘
                                         │
                                         ▼
                               ┌───────────────────┐
                               │   TALE COMPLETE   │
                               │   → Unlock Tale 2 │
                               └───────────────────┘
```

### Encounter Mix Per Chapter (Variety Guarantee)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CHAPTER COMPOSITION RULES                                                  │
│  ═══════════════════════                                                    │
│                                                                             │
│  Each chapter MUST include encounters from at least 3 different categories: │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Chapter 1 (Intro)     Chapter 2 (Core)      Chapter 3 (Advanced)   │  │
│  │  ─────────────────     ────────────────      ──────────────────     │  │
│  │  • 1 TOUR              • 1 WALKTHROUGH       • 1 HUNT or CRAFT      │  │
│  │  • 1 FLASH             • 1 FORK or DUEL      • 1 GAMBIT             │  │
│  │  • 1 LOOKUP            • 1 RACE or CRAFT     • 1 PUZZLE BOX         │  │
│  │                        • 1 REPAIR            • 1 SIEGE (optional)   │  │
│  │                                                                      │  │
│  │  Feel: Safe, guided    Feel: Choices matter  Feel: You're ready     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ANTI-MONOTONY RULE: Never 3 of same skeleton in sequence                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Campaign-Level Branching

```
                           ═══════════════════════════
                              CAMPAIGN: THE DREAD CITADEL
                           ═══════════════════════════
                                        │
                                        ▼
                              ┌──────────────────┐
                              │     TALE 1       │
                              │ "The Wanderer's  │
                              │    Arrival"      │
                              │  (ONBOARDING)    │
                              └────────┬─────────┘
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                  ┌──────────────┐          ┌──────────────┐
                  │    TALE 2A   │    OR    │    TALE 2B   │
                  │  "The Outer  │          │  "The Lower  │
                  │   Walls"     │          │   Vaults"    │
                  │ (Dictionary) │          │ (Analysis)   │
                  └──────┬───────┘          └──────┬───────┘
                         │                         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                              ┌──────────────────┐
                              │     TALE 3       │
                              │  "The Inner      │
                              │   Sanctum"       │
                              │ (INTERMEDIATE)   │
                              └────────┬─────────┘
                                       │
                      ┌────────────────┼────────────────┐
                      ▼                ▼                ▼
              ┌────────────┐   ┌────────────┐   ┌────────────┐
              │  TALE 4A   │   │  TALE 4B   │   │  TALE 4C   │
              │ "Brute     │   │ "Pattern   │   │ "The       │
              │  Force     │   │  Mastery"  │   │  Library"  │
              │  Tower"    │   │  (Masks)   │   │  (Rules)   │
              │  (Power)   │   │            │   │            │
              └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
                    │                │                │
                    └────────────────┴────────────────┘
                                     │
                                     ▼
                              ┌──────────────────┐
                              │     TALE 5       │
                              │  "The Throne     │
                              │   Room"          │
                              │ (BOSS / FINAL)   │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  CAMPAIGN END    │
                              │  → Unlock next   │
                              │    campaign or   │
                              │    Challenge     │
                              │    Dungeons      │
                              └──────────────────┘
```

---

## Skeleton Distribution Across 100 Encounters

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SKELETON USAGE (Ensuring Variety)                                          │
│  ══════════════════════════════════                                         │
│                                                                             │
│  FLASH        ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  12 encounters        │
│  LOOKUP       ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8 encounters        │
│  TOUR         ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   6 encounters        │
│  WALKTHROUGH  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  12 encounters        │
│  HUNT         ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10 encounters        │
│  CRAFT        ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10 encounters        │
│  RACE         ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   6 encounters        │
│  SIEGE        ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   4 encounters        │
│  FORK         ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8 encounters        │
│  GAMBIT       ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   6 encounters        │
│  PUZZLE BOX   ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   4 encounters        │
│  DUEL         ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   6 encounters        │
│  REPAIR       ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8 encounters        │
│  ─────────────────────────────────────────────────────────────────         │
│  TOTAL                                                100 encounters        │
│                                                                             │
│  Distribution ensures:                                                      │
│  • No skeleton > 12% of total                                              │
│  • Every skeleton used at least 4 times                                    │
│  • Mix of quick (FLASH/LOOKUP) and deep (SIEGE/PUZZLE BOX)                │
│  • Balance of guided (TOUR/WALK) and open (HUNT/CRAFT)                    │
│  • Meaningful choices present (FORK/GAMBIT/DUEL)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Skeleton Selection Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  "WHAT SKELETON DO I USE?"                                                  │
│  ══════════════════════════                                                 │
│                                                                             │
│  Teaching recognition/identification?     → FLASH                          │
│  Teaching how to find information?        → LOOKUP                         │
│  Introducing new tool/concept?            → TOUR                           │
│  Teaching a process/workflow?             → WALKTHROUGH                    │
│  Testing resourcefulness?                 → HUNT                           │
│  Testing creativity/synthesis?            → CRAFT                          │
│  Adding time pressure?                    → RACE                           │
│  Demonstrating progressive attack?        → SIEGE ⚠️                       │
│  Offering meaningful choice?              → FORK                           │
│  Teaching risk assessment?                → GAMBIT                         │
│  Multi-step mystery/unlock?               → PUZZLE BOX                     │
│  Teaching trade-off analysis?             → DUEL                           │
│  Teaching debugging/troubleshooting?      → REPAIR                         │
│  Teaching command chaining?               → PIPELINE                       │
│  Teaching automation?                     → SCRIPT                         │
│                                                                             │
│  ⚠️ SIEGE is only skeleton where slow execution is intentional            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*"Variety is the forge that keeps learning sharp."*

— Mirth, The Gamewright
