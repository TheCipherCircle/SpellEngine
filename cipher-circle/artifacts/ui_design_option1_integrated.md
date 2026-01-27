# UI Design Option 1: Integrated Panel (Archived)

> *Saved for potential future "easy mode" or accessibility implementation*

## Concept

Single window with story/art on top, tool wizard on bottom. Progressive unlock of features through Tutorial Tales.

## Layout (60% monitor, ~140x50 chars)

```
┌─────────────────────────────────────────────────────────────────┐
│                        THE DREAD CITADEL                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │                    [ASCII ART / BANNER]                   │  │
│  │                                                           │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                           │  │
│  │  The Gatekeeper blocks your path. Its seal glows:         │  │
│  │                                                           │  │
│  │  HASH: 0d107d09f5bbe40cade3de5c71e9e9b7                    │  │
│  │  TYPE: MD5 (32 chars)                                     │  │
│  │                                                           │  │
│  │  "What might someone type when they just want IN?"        │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  FORGE TOOLS                                    [Tutorial: 3/7] │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Wordlist │ │  Masks   │ │  Crack   │ │ Identify │           │
│  │    ▼     │ │    ▼     │ │    ▼     │ │    ▼     │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                 │
│  > Enter answer: _                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Progressive Unlock System

### Tutorial Tales Sequence

| Step | Unlocks | Explanation Shown |
|------|---------|-------------------|
| 1 | Hash Identifier | "Hashes have signatures. MD5=32 chars, SHA1=40 chars..." |
| 2 | Wordlist Viewer | "Wordlists contain known passwords from breaches..." |
| 3 | Quick Crack | "Enter a hash, get the plaintext if it's common..." |
| 4 | Mask Builder | "Masks describe patterns: ?l=lowercase, ?d=digit..." |
| 5 | Mask Crack | "Generate all possibilities matching a pattern..." |
| 6 | Combo Mode | "Combine wordlists with masks for hybrid attacks..." |
| 7 | Full Access | All tools unlocked, achievement awarded |

### Achievement

**"Forge Initiate"** - Complete the Tutorial Tales

### Skip Tutorial Behavior

If player skips tutorial or starts non-tutorial campaign:
- All tools available immediately
- No explanatory popups
- Achievement still earnable by going back

## Guardrail Analysis Needed

Count encounters where we'd want to restrict:
- [ ] Encounters that should only allow wordlist thinking
- [ ] Encounters that should only allow mask thinking
- [ ] Boss encounters with all tools
- [ ] Tutorial-specific restrictions

## Why Archived

- More UI complexity than Option 2
- Requires custom tool wizard implementation
- Less authentic "real tool" experience
- May revisit for accessibility or "guided mode"

---

*Archived 2025-01-24 for potential future use*
