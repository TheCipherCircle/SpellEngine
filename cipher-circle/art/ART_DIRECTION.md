# PatternForge Art Direction

**Established:** 2026-01-25 (Art Meeting)
**Style Reference:** Crawl by Powerhoof
**Quality Ceiling:** LucasArts (Day of the Tentacle, Full Throttle, Sam & Max)

---

## 1. Visual Identity

### Primary Style: "Crawl-Inspired Pixel Art"

We are creating **our own flavor** of Crawl's aesthetic:
- Same detail level and resolution philosophy
- Our own characters, monsters, and color palette
- The tone and feeling of Crawl's art
- Unique to PatternForge/Hashtopia universe

### Key Principles (from Crawl)

| Principle | Implementation |
|-----------|----------------|
| **Ultra-low resolution** | ~150px screen height, sprites 5-10px (monsters) to 20-30px (heroes) |
| **High-fidelity animation** | Many frames despite low res - smooth, fluid motion |
| **Motion blur smears** | Action happens BETWEEN frames, smear indicates movement |
| **Readable silhouettes** | Every character identifiable by shape alone |
| **Nostalgic filter** | Animate how we IMAGINED old games looked |
| **Efficiency** | Simple enough to iterate quickly, complex enough to impress |

### Color Philosophy

- **Base:** Muted earth tones (browns, tans, grays)
- **Accents:** Warm glows (fire, magic), cool highlights (steel, ice)
- **Per-character:** 2-3 signature colors each
- **Coordinated:** Complementary where it works, all on theme
- **Gruvbox influence:** Our existing terminal palette can inform choices

---

## 2. Asset Categories

### 2.1 Cover Art / Splash Screen

**Purpose:** First thing players see in all modes that need it
**Concept:** "The cover of the book you're about to open"
**Elements:**
- Title: "PatternForge" or campaign name
- Atmospheric background (forge, citadel, etc.)
- "Press [X] to Start" prompt
- Mood-setting imagery

**Needed:**
- [ ] Main PatternForge splash
- [ ] Dread Citadel campaign splash
- [ ] Future campaign splashes (template)

### 2.2 Team Portrait: Cipher Circle

**Format:** 3x3 grid (like TF2 character sheet reference)
**Also Create:** Campfire scene version for other media

| Member | Silhouette Hook | Colors | Pose |
|--------|-----------------|--------|------|
| **pitl0rd** | Hood, glowing eyes | Black, deep red, ember glow | Arms crossed, commanding |
| **Forge** | Apron, hammer | Bronze, orange, soot gray | Hammer resting on shoulder |
| **Mirth** | Jester hat, cards | Purple, gold, teal | Tossing dice/cards |
| **Loreth** | Robes, large book | Deep blue, cream, gold trim | Reading or pointing to text |
| **Vex** | Flowing cosmic cloak | Navy, star-white sparkles | Looking upward, gesturing |
| **Prism** | Crystal headpiece | White, rainbow refractions | Examining glowing object |
| **Anvil** | Heavy plate, shield | Steel gray, red accents | Solid stance, shield ready |
| **Fraz** | Beret, paintbrush | Splattered colors, earth base | Mid-brushstroke pose |
| **Jinx** | Circuit patterns, half-mask | Electric blue, black, silver | Mysterious, one eye visible |

**Campfire Scene Layout:**
- Simplified dark forest/ruins backdrop (muted, atmospheric)
- Central campfire as light source (warm glow on faces)
- 9 characters arranged naturally (some sitting, some standing)
- pitl0rd center-back (leader position)
- Forge tending fire
- Mirth animated/telling story
- Others in relaxed but characteristic poses

### 2.3 Pygame Mode Assets

**Resolution Target:** 512x384 for scenes, 64x64 for sprites

#### Characters (Sprites)
- [ ] Player character (multiple classes?)
- [ ] NPCs (quest givers, merchants)
- [ ] Enemies by tier (T1-T6)

#### Dread Citadel Campaign
- [ ] Chapter cards (3): Outer Gates, Crypts, Inner Sanctum
- [ ] Encounter backgrounds (~24)
- [ ] Boss sprites: Gatekeeper, Citadel Lord
- [ ] Environmental props: gates, locks, treasure, traps

#### UI Elements
- [ ] Achievement badges (64x64)
- [ ] Status icons (health, XP, etc.)
- [ ] Menu backgrounds
- [ ] Dialog boxes

### 2.4 README Graphics

**Style:** Fantasy forge themed

- [ ] Hero banner (PatternForge logo with forge/anvil imagery)
- [ ] Architecture diagram (SCARAB → EntropySmith as fantasy map)
- [ ] Prism handling data visualizations

---

## 3. Art Pipeline

### Story → Art Workflow

```
1. STORY CONTENT
   └── Created and pushed to Obsidian vault (100.tales)

2. ART TEAM ANALYSIS
   └── Reviews story content
   └── Develops questions for designer

3. DESIGNER MEETING
   └── Final details confirmed
   └── All enabling info collected

4. ART CREATION
   └── Art team creates 3 samples

5. APPROVAL MEETING
   └── Review with designer
   └── Iterate until approved

6. PRODUCTION
   └── Authorization given
   └── Full asset creation
```

### Who Creates What

| Asset Type | Creator | Method |
|------------|---------|--------|
| ASCII art | Fraz (internal) | Hand-crafted |
| Architecture diagrams | Prism (internal) | Data viz tools |
| Pixel art sprites | AI + Human review | PixelLab, Leonardo, Firefly |
| Scene backgrounds | AI + Human review | Prompt-based generation |
| Complex illustrations | Human artist | Commission (see brief) |

### AI Generation Strategy

**Primary Tools:**
1. [PixelLab](https://www.pixellab.ai/) - Game-ready sprites, Aseprite plugin
2. [Leonardo AI](https://leonardo.ai/) - 8-bit/16-bit specialized model
3. Adobe Firefly - Via designer (Pete) with prompts we create

**Prompt Template:**
```
16-bit pixel art [subject], Crawl game style,
[specific details], chibi proportions (for characters),
dark outlines, limited color palette [2-3 colors],
muted earth tones with [accent color] highlights,
transparent background, game sprite
```

**Prompt Keywords:**
- Style: "Crawl game style", "Powerhoof aesthetic", "dungeon crawler pixel art"
- Resolution: "16-bit", "low-res high-animation", "retro game sprite"
- Mood: "dark fantasy", "dungeon atmosphere", "torchlit", "muted earth tones"
- Technical: "transparent background", "sprite sheet", "game-ready asset"

---

## 4. Style Reference Library

### Primary Reference: Crawl (Powerhoof)
- [Steam Page](https://store.steampowered.com/app/293780/Crawl/)
- [Art Deep Dive](https://www.gamedeveloper.com/design/game-design-deep-dive-creating-the-striking-pixel-art-of-i-crawl-i-)
- [Art Process Video](https://www.powerhoof.com/crawl-art-process-vid-1/)

### Secondary References (LucasArts Quality Ceiling)
- Day of the Tentacle
- Full Throttle
- Sam & Max Hit the Road

### Sample Images (Local)
- `/Users/petermckernan/Downloads/bestexample.gif` - Scene composition, scale contrast
- `/Users/petermckernan/Downloads/pixel animations.gif` - Character sheet layout, chibi proportions

---

## 5. Deliverables Checklist

### Phase 1: Team Identity
- [ ] Cipher Circle 3x3 grid portrait
- [ ] Cipher Circle campfire scene
- [ ] Individual character sprites (9)

### Phase 2: Game Infrastructure
- [ ] PatternForge splash screen
- [ ] Dread Citadel splash screen
- [ ] Main menu background

### Phase 3: Dread Citadel Assets
- [ ] Chapter cards (3)
- [ ] Encounter backgrounds (24)
- [ ] Boss sprites (2)
- [ ] Enemy sprites by tier
- [ ] Props and environmental art

### Phase 4: Polish
- [ ] Achievement badges
- [ ] UI elements
- [ ] README graphics
- [ ] Animation frames for key sprites

---

## 6. Human Artist Brief

**Location:** To be added to Hashtopia-PatternForge vault

**Summary for External Artist:**

We need pixel art assets for a fantasy-themed password cracking education game.

**Style:** Crawl (by Powerhoof) - ultra-low resolution with high-fidelity animation feel. Muted earth tones, dark outlines, readable silhouettes.

**Scope:**
- 9-character team portrait (fantasy adventurer party)
- Game splash screens
- Campaign encounter art (~24 scenes)
- Character/enemy sprites

**References:** Crawl, Day of the Tentacle, Full Throttle

**Budget:** TBD
**Timeline:** TBD

---

*Document created from Art Meeting 2026-01-25*
*Attendees: pitl0rd (Designer), Forge (Engineering), Fraz (Art Lead)*
