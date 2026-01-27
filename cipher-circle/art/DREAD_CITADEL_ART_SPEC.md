# Dread Citadel Art Specification

**Campaign:** The Dread Citadel
**Style:** Crawl-inspired pixel art (Powerhoof)
**Approved:** 2026-01-25

---

## Design Decisions (Approved)

### Player Character
- **Visibility:** Visible sprite on screen
- **Archetype:** Hooded apprentice/rogue
- **Vibe:** Mysterious, shadowy, learning the craft
- **Colors:** Dark cloak, subtle glow from cipher knowledge

### Boss/Enemy Style
- **Direction:** Classic fantasy undead
- **Gatekeeper:** Ghostly knight with key/lock motifs
- **Crypt Guardian:** Spectral warrior, sword and shield
- **Left Hand / Right Hand:** Matching guardian pair, knight aesthetics
- **Citadel Lord:** **MASSIVE** (fills half screen), dark lord on throne of crystallized hashes

### Environment
- **Mood:** Dark fantasy (stone, shadows, torchlight)
- **Classic dungeon crawler aesthetic with hash integration**

### Hash Visualization
- **Context-dependent:**
  - Locks: Carved into stone
  - Lore moments: Written on scrolls/parchment
  - Magic/power: Floating glowing text
- **Hash type colors:**
  - MD5 = Amber/Orange glow
  - SHA1 = Blue/Cyan glow

### Lock Design
- **Variety throughout campaign:**
  - Physical metal locks with hash inscriptions
  - Magical seals/barriers that shatter
  - Ancient puzzle mechanisms (combination wheels)

### Chapter Cards
- **Style:** Full scene illustration (like book chapter headers)
- **Distinct color themes:**

| Chapter | Theme | Colors |
|---------|-------|--------|
| Ch1: Outer Gates | Weathered fortress at dusk | Stone gray, sunset orange, iron |
| Ch2: The Crypts | Underground tombs | Blue-green moss glow, darkness, bone white |
| Ch3: Inner Sanctum | Throne room of power | Deep purple, gold, crystalline highlights |

### Art Display (Pygame)
- **Varies by encounter type:**
  - `tour` = Minimal art, text-focused
  - `flash` = Split view (art | text)
  - `boss` = Full screen art, dramatic presentation
  - `gambit` = Split with choice indicators

---

## Asset List (Production Ready)

### Priority 1: Splash + Chapter Cards (4 images)

| Asset | Dimensions | Description |
|-------|------------|-------------|
| `splash_dread_citadel.png` | 1280x720 | Title screen - dark fortress silhouette, "THE DREAD CITADEL", "Press Enter to Begin" |
| `chapter_outer_gates.png` | 512x384 | Massive weathered gates at sunset, cryptic symbols glowing |
| `chapter_crypts.png` | 512x384 | Spiral stairs descending into phosphorescent darkness |
| `chapter_inner_sanctum.png` | 512x384 | Throne room doors flanked by spectral guards |

**Prompt template for splash:**
```
16-bit pixel art, dark fantasy castle silhouette against blood-red sunset,
Crawl game style, ominous fortress on cliff, muted earth tones with
orange/red sky highlights, gothic architecture, game title screen aesthetic
```

**Prompt template for chapter cards:**
```
16-bit pixel art dungeon scene, [chapter description], Crawl game style,
dark fantasy, torchlight illumination, [chapter color palette],
atmospheric perspective, game chapter card
```

---

### Priority 2: Boss Sprites (5 sprites)

| Asset | Size | Description |
|-------|------|-------------|
| `boss_gatekeeper.png` | 48x64 | Spectral knight, translucent, key/lock motifs on armor, amber glow |
| `boss_crypt_guardian.png` | 48x64 | Ghostly warrior, sword/shield, cyan accents |
| `boss_left_hand.png` | 32x48 | Armored guardian, scroll/book motif (wordlist) |
| `boss_right_hand.png` | 32x48 | Armored guardian, gear/pattern motif (mask) |
| `boss_citadel_lord.png` | 128x192 | **MASSIVE** dark lord, throne of hashes, purple/gold, menacing |

**Prompt template for bosses:**
```
16-bit pixel art boss sprite, [boss description], Crawl game style,
classic fantasy undead aesthetic, dark outlines, [boss colors],
transparent background, game enemy sprite, [size reference]
```

---

### Priority 3: Player Character (1 sprite + animations)

| Asset | Size | Description |
|-------|------|-------------|
| `player_apprentice.png` | 24x32 | Hooded rogue, dark cloak, subtle cipher glow, mysterious |

**Animation frames (if animated):**
- Idle (2-4 frames)
- Walk (4-6 frames)
- Victory pose
- Defeat pose

**Prompt template:**
```
16-bit pixel art character sprite, hooded apprentice rogue,
dark cloak, mysterious pose, Crawl game style, fantasy dungeon crawler hero,
dark outlines, muted colors with subtle glow, transparent background
```

---

### Priority 4: Location Backgrounds (11 scenes)

| Asset | Chapter | Description |
|-------|---------|-------------|
| `bg_valley_approach.png` | Ch1 | Standing stones in misty valley, path to fortress |
| `bg_outer_gates.png` | Ch1 | Massive stone gates, cryptic symbols, sunset light |
| `bg_servant_entrance.png` | Ch1 | Small side door, less grand, shadowy |
| `bg_inner_threshold.png` | Ch1 | Checkpoint alcove, torches, transition space |
| `bg_crypt_descent.png` | Ch2 | Spiral stairs, phosphorescent moss, carved warnings |
| `bg_pattern_weaver.png` | Ch2 | Alcove with loom of light, floating symbols |
| `bg_chamber_scrolls.png` | Ch2 | Library of parchments, warm candlelight glow |
| `bg_mask_forge.png` | Ch2 | Ethereal forge, smith of light, blazing possibility |
| `bg_deep_archive.png` | Ch2 | Vast hall, hashes organized on walls by type |
| `bg_sanctum_antechamber.png` | Ch3 | Two guardian statues, massive throne room doors |
| `bg_throne_room.png` | Ch3 | Crystallized hash throne, purple/gold grandeur |

**Dimensions:** 512x384 (pygame scene size)

---

### Priority 5: UI Elements

| Asset | Size | Description |
|-------|------|-------------|
| `lock_md5.png` | 64x64 | Physical lock with amber glow, 32-char hash carved |
| `lock_sha1.png` | 64x64 | Magical seal with cyan glow, 40-char hash |
| `lock_puzzle.png` | 64x64 | Combination wheel mechanism |
| `icon_xp.png` | 32x32 | Experience point indicator |
| `icon_checkpoint.png` | 32x32 | Save point marker |
| `panel_success.png` | 256x128 | "CRACKED!" celebration panel |
| `panel_failure.png` | 256x128 | "FAILED" defeat panel |

---

## Color Palettes

### Chapter 1: Outer Gates
```
Stone Gray:    #5C5C5C
Sunset Orange: #D4763E
Iron Dark:     #3D3D3D
Torch Yellow:  #E8B84A
Sky Dusk:      #8B5A6B
```

### Chapter 2: The Crypts
```
Moss Glow:     #4A8B6B
Deep Dark:     #1A1A2E
Bone White:    #E8E0D5
Cyan Accent:   #5BC0EB
Shadow Blue:   #2E4057
```

### Chapter 3: Inner Sanctum
```
Royal Purple:  #6B3FA0
Gold Accent:   #D4AF37
Crystal White: #F0F0FF
Dark Base:     #1E1024
Power Glow:    #9B59B6
```

### Hash Type Colors
```
MD5 Amber:     #E8A84A
MD5 Glow:      #FFD700
SHA1 Cyan:     #5BC0EB
SHA1 Glow:     #00FFFF
```

---

## Production Workflow

### Phase 1: Splash + Chapters (4 images)
1. Generate 3 samples per image using AI tools
2. Review meeting with designer
3. Select best, request refinements
4. Final approval
5. Export at correct dimensions

### Phase 2: Boss Sprites (5 sprites)
1. Character concept sketches (can be rough prompts)
2. Generate sprite variations
3. Select and refine
4. Ensure consistent style across all bosses
5. Citadel Lord gets extra attention (hero asset)

### Phase 3: Player + Backgrounds + UI
1. Player sprite (matches boss style)
2. Backgrounds in chapter order
3. UI elements last (functional priority)

---

## Prompt Cheat Sheet

**Style keywords (always include):**
- "16-bit pixel art"
- "Crawl game style" or "Powerhoof aesthetic"
- "dark fantasy dungeon"
- "dark outlines"
- "muted earth tones"

**For characters:**
- "chibi proportions" (for smaller sprites)
- "transparent background"
- "game sprite"

**For scenes:**
- "atmospheric"
- "torchlight illumination"
- "[chapter color palette]"
- "512x384 game scene"

**For bosses:**
- "classic fantasy undead"
- "spectral/ghostly"
- "menacing pose"

---

## File Naming Convention

```
assets/images/dread_citadel/
├── splash_dread_citadel.png
├── chapter_outer_gates.png
├── chapter_crypts.png
├── chapter_inner_sanctum.png
├── boss_gatekeeper.png
├── boss_crypt_guardian.png
├── boss_left_hand.png
├── boss_right_hand.png
├── boss_citadel_lord.png
├── player_apprentice.png
├── bg_valley_approach.png
├── bg_outer_gates.png
├── ... (etc)
├── lock_md5.png
├── lock_sha1.png
└── ui_*.png
```

---

## Next Steps

1. **Immediate:** Generate splash screen samples (3 variations)
2. **This week:** Chapter cards (3 images)
3. **Next:** Citadel Lord boss (hero asset)
4. **Then:** Remaining bosses, player, backgrounds

---

*Specification approved 2026-01-25*
*Designer: pitl0rd*
*Art Lead: Fraz*
