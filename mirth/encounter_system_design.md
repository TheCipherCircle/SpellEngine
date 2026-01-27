# PTHAdventures Encounter System Design
## Mirth's Game Design Document

**Created:** 2026-01-24
**Author:** Mirth, The Gamewright
**Status:** Design Phase

---

## Design Targets Summary

### Core Philosophy
- Encounters are **quick challenges** - focused, completable, satisfying
- Four encounter categories: Combat (cracking), Puzzle (analysis), Social (interpreting), Exploration (discovery)
- Progressive difficulty with clear tier unlocks
- Player profiles track progress and adapt difficulty
- Shell comfort is a primary goal (25% of content)

### CRITICAL: Designed Data Principles

**The Golden Rule:** Any designed data required for an instructive encounter MUST:
1. **Work** - The solution is achievable, tested, verified
2. **Work quickly** - No frustrating wait times unless the lesson IS about time
3. **Demonstrate the concept reliably** - The data proves the point every time

**Exception:** Progressive/iterative attack lessons (e.g., password failure cluster trends from Hashtopia) may intentionally take time to illustrate the attack pattern. These must be clearly labeled.

**Validation Chain:**
```
Mirth designs encounter → Axiom validates math/timing → Loreth provides lore links → Forgewright implements
```

**Data Requirements Per Encounter:**
- Hash cracks in < 5 seconds for Tier 0-3
- Hash cracks in < 30 seconds for Tier 4-5
- Tier 6 may involve longer runs if scripting/automation is the lesson
- All timing claims verified by Axiom before publication

### Modular Design Principle

**Encounter Skeletons:** Reusable structural templates that can be re-themed across campaigns.

The "shape" of an encounter is separate from its "skin":
- **Shape:** The mechanical structure (identify hash → explain reasoning → verify)
- **Skin:** The narrative wrapper (tavern mystery vs dungeon trap vs guild test)

This allows:
- One skeleton to power multiple encounters across campaigns
- Consistent difficulty within skeleton types
- Easier testing and validation
- Rapid content creation for new campaigns

### Distribution Targets (100 Encounters)

| Tier | % | Count | Type | Victory Condition |
|------|---|-------|------|-------------------|
| 0 | 10% | 10 | Very Easy | Direct Hashtopia link provides answer |
| 1 | 10% | 10 | Easy | PatternForge `--help` provides answer |
| 2 | 10% | 10 | Onboarding | Knowledge check (quiz/verification) |
| 3 | 10% | 10 | Guided | Wizard mode, simple options |
| 4 | 20% | 20 | Intermediate | Wizard mode + config, Hashtopia breadcrumbs |
| 5 | 25% | 25 | Shell Comfort | Terminal-native problem solving |
| 6 | 5% | 5 | Advanced | CLI chaining, scripting, complex workflows |

**Total: 100 encounters**

---

## Encounter Template

```yaml
# Encounter Definition Schema
encounter:
  id: "T1-C02-E03"  # Tier-Chapter-Encounter
  title: "The Whispering Hash"

  # Classification
  tier: 1  # 0-6 difficulty tier
  category: "puzzle"  # combat | puzzle | social | exploration
  estimated_minutes: 5

  # Narrative
  story:
    hook: "A mysterious hash appears on the tavern wall..."
    context: "The innkeeper says it appeared overnight."
    flavor: "The chalk marks seem to shimmer in candlelight."

  # Technical Content
  challenge:
    type: "identification"  # identification | cracking | analysis | scripting
    objective: "Identify the hash type"
    setup:
      provided_data: "5f4dcc3b5aa765d61d8327deb882cf99"
      environment: "terminal"  # terminal | wizard | web

    # Victory conditions
    victory:
      method: "command"  # command | answer | file | script
      expected: "patternforge identify 5f4dcc3b..."
      validation: "output contains 'MD5'"
      partial_credit: false

  # Help System
  hints:
    - level: 1
      cost: 0
      text: "What do you know about hash lengths?"
    - level: 2
      cost: 5
      text: "32 hex characters is a common signature..."
    - level: 3
      cost: 10
      link: "hashtopia://hash-types/md5"

  # Rewards
  rewards:
    first_clear:
      points: 100
      badge: "hash_whisperer"
    repeat_clear:
      points: 10
    speed_bonus:
      threshold_seconds: 60
      multiplier: 1.5

  # Dependencies
  prerequisites:
    encounters: []  # encounter IDs that must be completed
    tier_minimum: 0
    skills: []  # skill tags required

  # Metadata
  tags:
    - "hash-identification"
    - "md5"
    - "beginner"
  learning_objectives:
    - "Recognize MD5 by length and format"
    - "Use PatternForge identify command"
  hashtopia_links:
    - "hash-types/md5"
    - "tools/identification"
```

---

## Player Profile Schema

```yaml
# Player Save File: ~/.pthadventures/profile.yaml
player:
  # Identity (created during onboarding)
  name: "Wanderer"
  title: "Seeker of Secrets"
  class: "Apprentice Cryptomancer"
  created: "2026-01-24T10:30:00Z"

  # Character Stats (earned through play)
  stats:
    insight: 2      # Puzzle solving, pattern recognition
    precision: 1    # Exact command execution
    persistence: 3  # Completing difficult challenges
    wisdom: 2       # Knowledge retention (quiz scores)

  # Progression
  progression:
    current_tier: 2
    total_points: 1250
    tier_points:
      0: 500   # max 500, complete
      1: 500   # max 500, complete
      2: 250   # max 500, in progress
      3: 0
      4: 0
      5: 0
      6: 0

  # Completion Tracking
  encounters:
    completed:
      - id: "T0-C01-E01"
        first_clear: "2026-01-24T10:35:00Z"
        attempts: 1
        points_earned: 100
        time_seconds: 45
      - id: "T0-C01-E02"
        first_clear: "2026-01-24T10:42:00Z"
        attempts: 2
        points_earned: 85
        time_seconds: 180
    in_progress:
      - id: "T2-C01-E03"
        started: "2026-01-24T11:00:00Z"
        attempts: 1
        hints_used: 1

  # Achievements
  badges:
    - id: "first_blood"
      name: "First Blood"
      earned: "2026-01-24T10:35:00Z"
    - id: "hash_whisperer"
      name: "Hash Whisperer"
      earned: "2026-01-24T10:42:00Z"

  # Preferences
  settings:
    show_hints: true
    difficulty_scaling: "adaptive"  # adaptive | fixed | challenge
    shell_preference: "bash"  # bash | zsh | fish
```

---

## Progression System Options

### Option A: Gradient Unlock (Recommended)

**How it works:**
- Complete X% of encounters at Tier N to unlock Tier N+1
- Clear thresholds provide structure
- Players can't skip fundamentals

```
Tier 0 → Tier 1: Complete 8/10 (80%)
Tier 1 → Tier 2: Complete 8/10 (80%)
Tier 2 → Tier 3: Complete 8/10 (80%)
Tier 3 → Tier 4: Complete 15/20 (75%)
Tier 4 → Tier 5: Complete 18/25 (72%)
Tier 5 → Tier 6: Complete 4/5 (80%)
```

**Pros:**
- Ensures foundational knowledge
- Clear progression path
- Prevents frustration from premature difficulty

**Cons:**
- May feel restrictive to experienced users
- Requires good tier placement of content

---

### Option B: Point Threshold System

**How it works:**
- All encounters award points based on difficulty
- Point thresholds unlock tiers
- Allows flexible path through content

```
Points Required:
Tier 1: 300 points
Tier 2: 800 points
Tier 3: 1,500 points
Tier 4: 3,000 points
Tier 5: 6,000 points
Tier 6: 10,000 points
```

**Point Awards by Tier:**
| Tier | First Clear | Repeat | Speed Bonus |
|------|-------------|--------|-------------|
| 0 | 50 | 5 | 1.2x |
| 1 | 75 | 8 | 1.3x |
| 2 | 100 | 10 | 1.4x |
| 3 | 150 | 15 | 1.5x |
| 4 | 250 | 25 | 1.5x |
| 5 | 400 | 40 | 1.5x |
| 6 | 750 | 75 | 2.0x |

**Pros:**
- Flexible progression
- Rewards mastery (speed bonuses)
- Experienced users can advance quickly

**Cons:**
- Could skip important fundamentals
- Requires careful point balancing

---

### Option C: Hybrid System (Best of Both)

**How it works:**
- Points unlock tiers BUT
- Each tier has "gate encounters" that must be completed
- Gate encounters test core competencies

```
Tier Unlock Requirements:
- Meet point threshold AND
- Complete gate encounter(s) for that tier

Gate Encounters:
Tier 1 Gate: "Identify 3 hash types correctly"
Tier 2 Gate: "Answer 5 knowledge check questions"
Tier 3 Gate: "Complete a wizard-guided crack"
Tier 4 Gate: "Configure a custom attack"
Tier 5 Gate: "Solve a problem entirely in shell"
Tier 6 Gate: "Chain two CLI tools successfully"
```

**Pros:**
- Flexibility with quality gates
- Can't game past fundamentals
- Validates actual skill acquisition

**Cons:**
- More complex to implement
- Gate design is critical

---

### Recommendation: Option C (Hybrid)

The hybrid approach provides:
1. **Freedom** - Multiple paths through content
2. **Quality Control** - Gate encounters verify competency
3. **Motivation** - Points provide tangible progress
4. **Skill Verification** - Can't advance without demonstrating ability

---

## Difficulty Scaling Formula

### Base Difficulty Rating (BDR)

Each encounter has a Base Difficulty Rating from 1-100:

```
BDR = (tier_weight * 15) + (complexity_score) + (time_pressure) + (tool_count * 5)

Where:
- tier_weight: 0-6 (encounter tier)
- complexity_score: 0-25 (subjective design rating)
- time_pressure: 0-10 (is speed important?)
- tool_count: 1-5 (how many tools/concepts involved)
```

**Example Calculations:**

Tier 0 - "Read the Hashtopia page":
```
BDR = (0 * 15) + 5 + 0 + (1 * 5) = 10
```

Tier 3 - "Use wizard to configure attack":
```
BDR = (3 * 15) + 15 + 5 + (2 * 5) = 75
```

Tier 6 - "Script a multi-tool workflow":
```
BDR = (6 * 15) + 25 + 10 + (4 * 5) = 145 → capped at 100
```

### Adaptive Difficulty (Player-Relative)

```
Effective_Difficulty = BDR * (1 + player_modifier)

player_modifier = (total_points / 10000) * 0.5
```

A player with 5000 points faces 1.25x effective difficulty on repeat content.
This prevents farming and encourages progression.

---

## The 100 Encounters

### Tier 0: Very Easy (10 encounters)
*Direct Hashtopia link provides answer*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T0-01 | The Tavern Notice | exploration | Read about hash types on Hashtopia |
| T0-02 | The Merchant's Riddle | puzzle | Look up MD5 characteristics |
| T0-03 | The Scribe's Question | social | Find the definition of "salt" |
| T0-04 | Whispers of SHA | exploration | Learn SHA-1 vs SHA-256 difference |
| T0-05 | The Apprentice's First Lesson | social | What is a rainbow table? |
| T0-06 | Symbols on the Wall | puzzle | Find common hash lengths chart |
| T0-07 | The Elder's Memory | social | What is bcrypt? |
| T0-08 | Patterns in the Dust | exploration | Learn about wordlists |
| T0-09 | The Keeper's Warning | social | Read about responsible disclosure |
| T0-10 | The Map Room | exploration | Navigate Hashtopia structure |

### Tier 1: Easy (10 encounters)
*PatternForge --help provides answer*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T1-01 | The Blade Awakens | exploration | Run `patternforge --help` |
| T1-02 | First Words | combat | Use `patternforge identify` |
| T1-03 | The Listing | exploration | List available commands |
| T1-04 | Corpus Discovery | exploration | Learn about `ingest` command |
| T1-05 | The Analyzer's Path | puzzle | Find `analyze` options |
| T1-06 | Forge Parameters | exploration | Explore `forge` help |
| T1-07 | Export Secrets | puzzle | Discover export formats |
| T1-08 | The Report Scroll | exploration | Learn `report` command |
| T1-09 | Version Check | combat | Display version info |
| T1-10 | Configuration Paths | exploration | Find config file location |

### Tier 2: Onboarding Knowledge Checks (10 encounters)
*Quiz/verification of understanding*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T2-01 | The Three Pillars | social | Explain Hashtopia/PatternForge/PTHAdventures |
| T2-02 | Hash or Password? | puzzle | Distinguish hash from plaintext |
| T2-03 | Length Matters | puzzle | Identify hash type by length |
| T2-04 | The Salt Question | social | Explain why salting matters |
| T2-05 | Wordlist Wisdom | puzzle | Choose appropriate wordlist size |
| T2-06 | Attack Vectors | social | Name three attack types |
| T2-07 | The Time Cost | puzzle | Estimate relative crack times |
| T2-08 | Legal Boundaries | social | Identify authorized testing scenarios |
| T2-09 | The SCARAB Way | puzzle | Explain what SCARAB analyzes |
| T2-10 | EntropySmith's Gift | social | Describe candidate generation |

### Tier 3: Wizard Mode - Simple (10 encounters)
*Guided wizard with simple options*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T3-01 | The Gentle Guide | combat | Complete wizard-guided identify |
| T3-02 | Wordlist Selection | puzzle | Choose wordlist via wizard |
| T3-03 | Simple Ingest | combat | Ingest corpus with wizard |
| T3-04 | Basic Analysis | puzzle | Run SCARAB via wizard |
| T3-05 | First Forge | combat | Generate candidates with defaults |
| T3-06 | Export Basics | combat | Export to Hashcat format |
| T3-07 | The Quick Report | puzzle | Generate summary report |
| T3-08 | Profile Setup | exploration | Configure user preferences |
| T3-09 | Output Paths | puzzle | Set output directory |
| T3-10 | The Practice Hash | combat | Crack provided practice hash |

### Tier 4: Wizard Mode - Configured (20 encounters)
*Configuration options + Hashtopia breadcrumbs*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T4-01 | Mask Crafting | puzzle | Configure mask attack |
| T4-02 | Rule Selection | puzzle | Choose rule set with rationale |
| T4-03 | Budget Limits | combat | Set candidate budget |
| T4-04 | Length Constraints | puzzle | Configure min/max length |
| T4-05 | Character Classes | puzzle | Require specific char types |
| T4-06 | The Hybrid Approach | combat | Combine wordlist + mask |
| T4-07 | Policy Filters | puzzle | Apply password policy rules |
| T4-08 | Entropy Thresholds | puzzle | Set entropy requirements |
| T4-09 | Distribution Sampling | combat | Configure sampling strategy |
| T4-10 | Grammar Expansion | puzzle | Use grammar-based generation |
| T4-11 | Token Analysis | puzzle | Interpret SCARAB token output |
| T4-12 | Transition Patterns | puzzle | Understand state transitions |
| T4-13 | Custom Wordlists | combat | Ingest and analyze custom corpus |
| T4-14 | Benchmark Reading | puzzle | Interpret performance data |
| T4-15 | Attack Ordering | puzzle | Sequence multiple attacks |
| T4-16 | Resource Estimation | puzzle | Calculate time/space needs |
| T4-17 | The Salted Challenge | combat | Handle salted hashes |
| T4-18 | Multiple Hash Types | puzzle | Process mixed hash file |
| T4-19 | Output Formatting | puzzle | Configure report detail level |
| T4-20 | The Model Bundle | exploration | Understand ModelBundle contents |

### Tier 5: Shell Comfort (25 encounters)
*Terminal-native problem solving*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T5-01 | Pipe Dreams | combat | Pipe command output |
| T5-02 | File Wrangling | puzzle | Use head/tail/wc |
| T5-03 | The Grep Guardian | combat | Filter with grep |
| T5-04 | Sort and Unique | puzzle | Process duplicate lines |
| T5-05 | Redirect Mastery | combat | Output to file |
| T5-06 | Environment Variables | puzzle | Set and use env vars |
| T5-07 | Path Navigation | exploration | Navigate project structure |
| T5-08 | Permission Check | puzzle | Understand file permissions |
| T5-09 | Process Watching | exploration | Monitor running commands |
| T5-10 | The History Keeper | puzzle | Use command history |
| T5-11 | Alias Creation | puzzle | Create useful aliases |
| T5-12 | Tab Completion | exploration | Efficient command entry |
| T5-13 | Man Page Reading | puzzle | Find info in man pages |
| T5-14 | Error Streams | puzzle | Handle stderr vs stdout |
| T5-15 | Background Jobs | combat | Run commands in background |
| T5-16 | The Cut Master | puzzle | Extract fields with cut |
| T5-17 | AWK Basics | puzzle | Simple awk processing |
| T5-18 | Sed Introduction | combat | Basic sed substitution |
| T5-19 | Find and Act | combat | Use find with -exec |
| T5-20 | Archive Operations | puzzle | Compress/extract files |
| T5-21 | Network Basics | exploration | curl/wget fundamentals |
| T5-22 | JSON Parsing | puzzle | Use jq for JSON |
| T5-23 | The Loop | combat | Simple bash for loop |
| T5-24 | Conditional Logic | puzzle | if/then in shell |
| T5-25 | Functions | combat | Define shell function |

### Tier 6: Advanced CLI (5 encounters)
*Chaining tools, scripting, complex workflows*

| ID | Title | Category | Objective |
|----|-------|----------|-----------|
| T6-01 | The Pipeline Master | combat | Chain 3+ tools via stdin/stdout |
| T6-02 | The Automation | combat | Script a multi-step workflow |
| T6-03 | Batch Processing | puzzle | Process multiple files programmatically |
| T6-04 | The Integration | combat | Connect PatternForge to Hashcat flow |
| T6-05 | The Grand Workflow | combat | Complete ingest→analyze→forge→export→crack |

---

## Encounter Skeletons (Reusable Templates)

These are the mechanical "shapes" that can be skinned with any narrative theme.

### Skeleton: IDENTIFY
**Purpose:** Player identifies something (hash type, pattern, concept)
**Flow:** Present artifact → Player examines → Player states identification → Validate
**Tiers:** 0-2
**Designed Data:** Pre-selected hash with unambiguous type signature
**Timing:** Instant (lookup/recognition task)

```yaml
skeleton: IDENTIFY
inputs:
  artifact: "{{ hash_or_pattern }}"
  correct_answer: "{{ expected_identification }}"
  hint_link: "{{ hashtopia_page }}"
validation:
  type: "exact_match"  # or "contains"
designed_data_requirement: "Artifact must have single unambiguous answer"
```

---

### Skeleton: LOOKUP
**Purpose:** Player finds information in documentation
**Flow:** Ask question → Player searches → Player provides answer → Validate
**Tiers:** 0-1
**Designed Data:** None (uses existing Hashtopia/help content)
**Timing:** Instant (reading task)

```yaml
skeleton: LOOKUP
inputs:
  question: "{{ what_to_find }}"
  source: "hashtopia | help | man"
  correct_answer: "{{ expected_answer }}"
validation:
  type: "knowledge_check"
designed_data_requirement: "Answer must exist in source material"
```

---

### Skeleton: EXECUTE_SIMPLE
**Purpose:** Player runs a single command correctly
**Flow:** State objective → Player constructs command → Execute → Validate output
**Tiers:** 1-3
**Designed Data:** May need practice hash/file
**Timing:** < 5 seconds execution

```yaml
skeleton: EXECUTE_SIMPLE
inputs:
  objective: "{{ what_to_accomplish }}"
  target_data: "{{ file_or_hash }}"
  expected_command_pattern: "{{ regex_or_exact }}"
  expected_output_contains: "{{ success_indicator }}"
validation:
  type: "command_output"
designed_data_requirement: "Target data must produce expected output reliably"
```

---

### Skeleton: WIZARD_GUIDED
**Purpose:** Player completes task using wizard interface
**Flow:** Launch wizard → Navigate options → Complete workflow → Validate result
**Tiers:** 3-4
**Designed Data:** Corpus or hash that works with default/simple settings
**Timing:** < 10 seconds for underlying operation

```yaml
skeleton: WIZARD_GUIDED
inputs:
  workflow: "ingest | analyze | forge | export"
  target_data: "{{ file_or_hash }}"
  required_choices: ["{{ option_1 }}", "{{ option_2 }}"]
  expected_result: "{{ success_file_or_output }}"
validation:
  type: "file_exists | output_matches"
designed_data_requirement: "Data must succeed with wizard defaults + minimal config"
```

---

### Skeleton: CONFIGURE_AND_EXECUTE
**Purpose:** Player makes configuration decisions then executes
**Flow:** Present scenario → Player configures options → Execute → Validate → Explain why
**Tiers:** 4-5
**Designed Data:** Data that responds differently to different configs
**Timing:** < 30 seconds execution

```yaml
skeleton: CONFIGURE_AND_EXECUTE
inputs:
  scenario: "{{ situation_description }}"
  target_data: "{{ file_or_hash }}"
  config_options:
    - name: "{{ option_name }}"
      choices: ["{{ a }}", "{{ b }}", "{{ c }}"]
      optimal: "{{ best_choice }}"
  expected_result: "{{ success_indicator }}"
  learning_point: "{{ why_this_config_matters }}"
validation:
  type: "result_quality"  # partial credit for suboptimal configs
designed_data_requirement: "Data must clearly demonstrate config impact"
```

---

### Skeleton: SHELL_TASK
**Purpose:** Player solves problem using shell commands (no PatternForge)
**Flow:** Present file/data problem → Player uses shell tools → Validate result
**Tiers:** 5
**Designed Data:** Text files with specific patterns to find/transform
**Timing:** Instant (shell operations)

```yaml
skeleton: SHELL_TASK
inputs:
  problem: "{{ what_needs_doing }}"
  input_file: "{{ starting_data }}"
  expected_output: "{{ result_file_or_stdout }}"
  allowed_tools: ["grep", "sort", "cut", "awk", "sed", "wc", "head", "tail"]
  hint_commands: ["{{ useful_command_1 }}", "{{ useful_command_2 }}"]
validation:
  type: "output_diff"
designed_data_requirement: "Input file crafted to exercise specific shell skills"
```

---

### Skeleton: PIPELINE
**Purpose:** Player chains multiple commands via stdin/stdout
**Flow:** Present multi-step problem → Player builds pipeline → Validate final output
**Tiers:** 5-6
**Designed Data:** Data requiring transformation chain
**Timing:** Instant (pipeline execution)

```yaml
skeleton: PIPELINE
inputs:
  problem: "{{ multi_step_objective }}"
  input_data: "{{ starting_point }}"
  minimum_pipe_count: 2
  expected_output: "{{ final_result }}"
  example_solution: "{{ one_valid_pipeline }}"  # for hints
validation:
  type: "output_match"  # any pipeline that produces correct output wins
designed_data_requirement: "Problem must genuinely require multiple transformations"
```

---

### Skeleton: SCRIPT
**Purpose:** Player writes a script to automate a task
**Flow:** Present repeatable problem → Player writes script → Execute on test data → Validate
**Tiers:** 6
**Designed Data:** Multiple test cases for script validation
**Timing:** Script execution < 30 seconds total

```yaml
skeleton: SCRIPT
inputs:
  problem: "{{ automation_objective }}"
  test_cases:
    - input: "{{ test_1_input }}"
      expected: "{{ test_1_output }}"
    - input: "{{ test_2_input }}"
      expected: "{{ test_2_output }}"
  language: "bash | python"
  starter_template: "{{ optional_scaffold }}"
validation:
  type: "test_case_pass_rate"
  minimum_pass: 0.8
designed_data_requirement: "Test cases cover edge conditions, all solvable"
```

---

### Skeleton: PROGRESSIVE_ATTACK
**Purpose:** Demonstrate iterative/time-based attack patterns
**Flow:** Set up attack → Run progressively → Observe pattern → Explain learning
**Tiers:** 4-6
**Designed Data:** Password set exhibiting target pattern (e.g., failure clusters)
**Timing:** INTENTIONALLY VARIABLE - this is the lesson

```yaml
skeleton: PROGRESSIVE_ATTACK
inputs:
  concept: "{{ what_pattern_to_demonstrate }}"
  password_set: "{{ designed_corpus }}"
  observation_points:
    - time: "{{ checkpoint_1 }}"
      expected_state: "{{ what_should_be_true }}"
    - time: "{{ checkpoint_2 }}"
      expected_state: "{{ progression_indicator }}"
  learning_point: "{{ why_this_pattern_matters }}"
validation:
  type: "observation_log"
designed_data_requirement: "Corpus MUST exhibit target pattern reliably"
warning: "TIMING IS PART OF THE LESSON - label clearly"
```

---

### Skeleton: KNOWLEDGE_CHECK
**Purpose:** Quiz player on concepts (no tool execution)
**Flow:** Present questions → Player answers → Score → Provide feedback
**Tiers:** 2
**Designed Data:** None (questions only)
**Timing:** Instant

```yaml
skeleton: KNOWLEDGE_CHECK
inputs:
  questions:
    - q: "{{ question_text }}"
      options: ["{{ a }}", "{{ b }}", "{{ c }}", "{{ d }}"]
      correct: "{{ correct_option }}"
      explanation: "{{ why_correct }}"
      hashtopia_link: "{{ reference_page }}"
  pass_threshold: 0.8
validation:
  type: "score"
designed_data_requirement: "Questions have unambiguous correct answers with Hashtopia backing"
```

---

### Skeleton Count: 10

These 10 skeletons can generate hundreds of encounters by varying:
- Narrative theme (campaign skin)
- Specific data (designed for each lesson)
- Difficulty tuning (timeouts, hint availability, partial credit)

---

## Encounter Categories Explained

### Combat (Cracking)
- Direct tool execution
- Hash identification and cracking
- Generating candidates
- Running attacks
- **Victory:** Successful command execution or hash recovery

### Puzzle (Analysis)
- Interpreting output
- Choosing strategies
- Understanding data
- Configuration decisions
- **Victory:** Correct answer/selection

### Social (Interpreting)
- Knowledge questions
- Concept explanations
- Ethical scenarios
- Community standards
- **Victory:** Demonstrate understanding

### Exploration (Discovery)
- Learning tool capabilities
- Navigating resources
- Finding information
- Understanding structure
- **Victory:** Locate/identify target information

---

## Implementation Notes

### File Structure
```
~/.pthadventures/
  profile.yaml           # Player save file
  progress/
    tier_0.yaml          # Completed encounters per tier
    tier_1.yaml
    ...
  achievements/
    badges.yaml          # Earned badges
  settings.yaml          # User preferences
```

### Validation Functions Needed
```python
def validate_encounter_complete(encounter_id, player_input, expected):
    """Check if player completed encounter correctly."""

def calculate_points(encounter, time_taken, hints_used):
    """Calculate points earned for completion."""

def check_tier_unlock(player_profile, target_tier):
    """Verify player can access requested tier."""

def update_player_stats(profile, encounter_result):
    """Update player stats based on encounter outcome."""
```

### Gate Encounter Specifications

| Tier | Gate ID | Requirement |
|------|---------|-------------|
| 1 | T1-GATE | Identify 3 hash types correctly |
| 2 | T2-GATE | Score 80% on 10-question quiz |
| 3 | T3-GATE | Complete wizard-guided workflow |
| 4 | T4-GATE | Configure and execute custom attack |
| 5 | T5-GATE | Solve problem using only shell commands |
| 6 | T6-GATE | Create working automation script |

---

## Summary of Design Targets

1. **100 encounters** across 7 difficulty tiers (0-6)
2. **Four categories:** Combat, Puzzle, Social, Exploration
3. **Distribution:** Heavy emphasis on shell comfort (25%) and intermediate wizard use (20%)
4. **Progression:** Hybrid system with point thresholds + gate encounters
5. **Player profiles:** YAML save files tracking progress, stats, and achievements
6. **Quick challenges:** Focused, completable, satisfying micro-experiences
7. **Learning integration:** Hashtopia links as breadcrumbs, not answers
8. **Shell-first mindset:** 30% of content (Tier 5+6) requires terminal proficiency
9. **Practical complexity:** Configuration options stay grounded, no over-engineering
10. **CLI mastery path:** Chaining → Scripting → Full workflow automation

---

---

## Complexity Review (Mirth's Honest Assessment)

### Currently Sound
- **10 skeletons** - Covers all encounter types without redundancy
- **YAML schemas** - Simple, human-readable, easy to validate
- **Tier system** - Clear progression, not overloaded
- **Point math** - Straightforward, Axiom can verify easily

### Watch List (May Need Simplification)

| Area | Concern | Recommendation |
|------|---------|----------------|
| Player stats (insight/precision/etc) | May be unnecessary complexity | Start without them, add if gameplay needs it |
| Adaptive difficulty formula | `player_modifier` math might overcomplicate | Test with fixed difficulty first |
| Speed bonus multipliers | Could create weird incentives | Keep simple: bonus yes/no, not sliding scale |
| Partial credit validation | Complex to implement reliably | V1: binary pass/fail only |

### Deferred Until Proven Needed
- Achievement/badge system (fun but not core)
- Detailed timing tracking per encounter
- Player stat progression
- Leaderboard integration

### Simplification Candidates

**Current:** Encounter IDs like `T1-C02-E03` (Tier-Chapter-Encounter)
**Simpler:** Just `encounter_042` with tier as metadata field

**Current:** Multiple validation types per skeleton
**Simpler:** One validation type per skeleton, choose skeleton by validation need

**Current:** Hints with cost system
**Simpler:** V1 hints are free, track usage for analytics only

---

## Agent Collaboration Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENCOUNTER DESIGN FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Mirth designs encounter skeleton + narrative skin           │
│           ↓                                                     │
│  2. Mirth specifies designed data requirements                  │
│           ↓                                                     │
│  3. Loreth (Scribe) provides Hashtopia links + lore check       │
│           ↓                                                     │
│  4. Axiom (MVA) validates:                                      │
│     - Timing claims ("cracks in < 5 sec")                       │
│     - Difficulty ratings match actual complexity                │
│     - Point awards are balanced                                 │
│     - Designed data will produce expected results               │
│           ↓                                                     │
│  5. Forgewright implements encounter in game engine             │
│           ↓                                                     │
│  6. Vexari (Cosmic) observes player behavior post-launch        │
│           ↓                                                     │
│  7. Feedback loop: Adjust based on observations                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Axiom's Validation Checklist:**
- [ ] All timing claims tested on reference hardware
- [ ] Difficulty rating matches measured complexity
- [ ] Designed data produces expected output 100% of the time
- [ ] Point values follow tier formula
- [ ] No impossible encounters (solvable paths exist)

**Loreth's Content Checklist:**
- [ ] All Hashtopia links are valid and current
- [ ] Lore references match canonical knowledge
- [ ] No contradictions with existing documentation
- [ ] Learning objectives align with Hashtopia structure

---

*"Every encounter is a door. Some lead to knowledge, some to skill, all lead forward."*

— Mirth, The Gamewright
