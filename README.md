# Storysmith

<!-- Hero banner placeholder -->
<!-- ![Storysmith Banner](docs/images/banner.png) -->

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red)
![Status: Active Development](https://img.shields.io/badge/status-active_development-yellow)

**The narrative engine that transforms security tools into immersive adventures.**

Storysmith is the premium experience layer for PatternForge, turning pattern analysis and password security concepts into engaging interactive campaigns with branching narratives, achievement systems, and a corrupted SNES visual aesthetic.

---

## What is Storysmith?

Storysmith is a **closed-source narrative engine** that sits atop [PatternForge](https://github.com/hashtopia/patternforge), transforming technical security concepts into playable adventures. Where PatternForge provides the analytical tools, Storysmith provides the journey.

> *"If they're not having fun, they're not learning."*
> *— The Cipher Circle*

The engine bridges the gap between abstract security knowledge and practical understanding through:

- **Interactive Campaigns** - Multi-chapter adventures with meaningful choices
- **Real Tool Integration** - PatternForge commands woven into gameplay
- **Adaptive Difficulty** - Encounters scale based on player progression
- **Rich Achievement Systems** - Track mastery across multiple dimensions

---

## Features

| Feature | Description |
|---------|-------------|
| **Campaign Engine** | Multi-tale adventures with branching paths and player-driven narratives |
| **Encounter Framework** | 13 encounter skeletons from quick FLASH challenges to epic SIEGE battles |
| **Achievement System** | Multi-tier progression tracking with badges and unlockables |
| **Experience Grading** | Sophisticated scoring that rewards both speed and accuracy |
| **Pygame Integration** | Game client with audio, scenes, and visual rendering |
| **ASCII Art Library** | Hand-crafted terminal art for atmosphere and polish |
| **Agent Architecture** | Mirth (narrative), Scribe (content), and Cosmic (patterns) agents |

---

## The Dread Citadel

*The flagship campaign.*

<!-- Campaign art placeholder -->
<!-- ![The Dread Citadel](assets/images/dread_citadel_banner.png) -->

**The Dread Citadel** is Storysmith's first complete campaign - a dark fantasy adventure where players learn password analysis by conquering an ancient fortress of broken secrets.

### Campaign Structure

```
THE DREAD CITADEL
       |
       v
  [Tale 1: The Wanderer's Arrival]     <- Onboarding
       |
   +---+---+
   v       v
[Outer  ] [Lower ]                     <- Choose your path
[Walls  ] [Vaults]
   +---+---+
       |
       v
  [Tale 3: The Inner Sanctum]          <- Intermediate challenges
       |
   +---+---+---+
   v   v   v
[Brute][Pattern][Library]              <- Specialization
[Force][Mastery][Rules  ]
   +---+---+---+
       |
       v
  [Tale 5: The Throne Room]            <- Boss encounter
       |
       v
    VICTORY
```

### Visual Aesthetic

Storysmith employs a **corrupted SNES** visual style inspired by Crawl (Powerhoof):

- Ultra-low resolution with high-fidelity feel
- Muted earth tones with accent glows
- Readable silhouettes and dark outlines
- Nostalgic filter - how we *imagined* retro games looked

---

## Architecture

Storysmith depends on PatternForge as its analytical foundation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            STORYSMITH                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │   Campaigns  │  │    Engine    │  │    Agents    │                   │
│  │  (Content)   │  │   (Pygame)   │  │  (AI/Logic)  │                   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │
│         │                 │                 │                           │
│         └─────────────────┴─────────────────┘                           │
│                           │                                             │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │
                            v
┌───────────────────────────────────────────────────────────────────────────┐
│                          PATTERNFORGE                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Ingest    │  │    SCARAB    │  │ EntropySmith │  │   Hashcat    │  │
│  │   (Corpus)   │  │  (Analysis)  │  │ (Generation) │  │  (Cracking)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
storysmith/
├── adventures/     # Adventure system (achievements, state, grading)
├── agents/         # AI agents (Mirth, Scribe, Cosmic, Math Validator)
├── campaigns/      # Campaign content and scripts
└── engine/         # Pygame game engine (audio, rendering, scenes)

cipher-circle/      # Team documentation and continuity
├── council/        # Agent profiles and work orders
├── chronicles/     # The Scholar's interviews
├── artifacts/      # Work products and designs
└── art/            # Art direction and specifications

mirth/              # Game design documentation
├── encounter_*.md  # Encounter system specs
└── pacing_*.md     # Rhythm and flow design

assets/             # Visual and audio assets
lore/               # Narrative documentation
```

---

## Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| PatternForge | Latest | Latest |
| Pygame | 2.0+ | 2.5+ |
| RAM | 2 GB | 4+ GB |

---

## The Cipher Circle

<!-- Team portrait placeholder -->
<!-- ![Cipher Circle](docs/images/cipher-circle.png) -->

Storysmith is built by the **Cipher Circle** - a 9-member human-AI development fellowship.

| Member | Title | Domain |
|--------|-------|--------|
| **pitl0rd** | Master of the Pit | Vision, Direction |
| **Forge** | The Artificer | Engineering, Architecture |
| **Mirth** | The Gamewright | Experience, Engagement |
| **Loreth** | The Lorekeeper | Documentation, Memory |
| **Vex** | The Cosmic | Ideas, Possibilities |
| **Prism** | The Revelator | Visualization, Patterns |
| **Anvil** | The Validator | Testing, Quality |
| **Fraz** | Pigment Alchemist | ASCII Art, Visuals |
| **Jinx** | Neural Architect | Machine Learning |

> *"Nine minds, one forge. The harmony is in the contrast."*

---

## Related Projects

| Project | Description | License |
|---------|-------------|---------|
| [PatternForge](https://github.com/hashtopia/patternforge) | Pattern-aware password analysis toolkit | Apache 2.0 |
| [Hashtopia](https://hashtopia.net) | Password security knowledge base | CC BY-NC |

---

## License

**Proprietary - All Rights Reserved**

Storysmith is closed-source software. This repository contains premium adventure content, the narrative engine, and game systems that are not open source.

For licensing inquiries, contact the Cipher Circle.

---

*Built with care by the Cipher Circle*
