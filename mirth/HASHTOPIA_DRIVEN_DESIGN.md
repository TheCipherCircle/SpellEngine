# Hashtopia-Driven Design Philosophy

## Core Principle

**All the answers are hidden here. No googling required.**

This is what makes the Cipher Circle ecosystem special. Players don't need external resources because:
- Passwords are generated FROM Hashtopia's patterns
- Tools (SCARAB, EntropySmith, PatternForge) analyze those same patterns
- Using the tools correctly reveals the answers naturally

The game is self-contained. The learning is authentic.

---

## First-Run Welcome Message

Display when player creates their first save:

```
Welcome to the Cipher Circle, Initiate.

Everything you need to succeed is already here.

The passwords you seek? Hidden in patterns.
The tools to find them? At your fingertips.
The knowledge to master them? Woven into every challenge.

No googling required. No external guides needed.
The answers are here. Learn to see them.

Press ENTER to begin your journey...
```

---

## Two Modes of Encounter Design

### Brittle Mode (Prologue Only)

**Use case:** Onboarding new players into the software

- Hand-crafted passwords with explicit narrative hints
- "The answer is literally in the question"
- Training wheels that teach interface, not methodology
- Examples: "password", "123456", "qwerty"

**Value:** Gets people comfortable with the game mechanics before introducing real analysis.

### Hashtopia-Driven Mode (All Other Chapters)

**Use case:** Teaching authentic password analysis methodology

- Passwords generated FROM Hashtopia corpus patterns
- Players discover answers through proper analysis
- Tools work because passwords ARE in the keyspace they analyze
- No hand-holding—methodology IS the solution

**Value:** Authentic learning. Skills transfer to real-world practice.

---

## Difficulty Implications

| Difficulty | Password Source | Discovery Method |
|------------|-----------------|------------------|
| **Normal** | Top 1000 corpus words, simple patterns | Basic wordlist attack |
| **Heroic** | Corpus combinations, light transforms | Masks + rule attacks |
| **Mythic** | Generated passphrases, heavy transforms | Full pipeline (SCARAB → EntropySmith) |

### Key Insight

Difficulty isn't about "harder passwords"—it's about "deeper keyspace":

- **Normal:** Surface patterns (rockyou top 1000)
- **Heroic:** Structural patterns (common masks)
- **Mythic:** Generated patterns (requires full toolchain)

---

## Encounter Design Shift

### Old Model (Brittle)
```yaml
- id: enc_gatekeeper
  solution: "letmein"
  hint: "A polite request for entry"
```

### New Model (Hashtopia-Driven)
```yaml
- id: enc_gatekeeper
  keyspace:
    source: "hashtopia/common_phrases"
    pattern: "VERB+PRONOUN+PREPOSITION"
    transforms: ["lowercase", "no_spaces"]
  discovery_method: "wordlist"
  hint_tier: 1  # Unlocks after 3 failed attempts
```

The password is generated at campaign-build time from the corpus.
Players find it by applying the right methodology to the right keyspace.

---

## Implementation TODO

1. [ ] Create Hashtopia corpus query API
2. [ ] Build password generator from corpus patterns
3. [ ] Define keyspace constraint schema for encounters
4. [ ] Implement first-run welcome popup in title.py
5. [ ] Migrate Chapter 1+ encounters to Hashtopia-driven model
6. [ ] Keep Prologue as brittle mode for onboarding

---

## The Promise

When a player completes the Dread Citadel, they haven't just "beaten a game."

They've learned a methodology that works in the real world—because the game
taught them using the same patterns and tools practitioners use.

**The game doesn't simulate password analysis. It IS password analysis.**
