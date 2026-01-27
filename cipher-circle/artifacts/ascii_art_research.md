# ASCII Art Deep Dive - Fraz's Research Notes

**Date:** 2026-01-25
**Sources:** SanctuaryRPG, Stone Story RPG, Cogmind, Dwarf Fortress, classic roguelikes
**Purpose:** Inform PatternForge visual style

---

## The Masters

### SanctuaryRPG
- **Style:** Dense, atmospheric, first-person perspective ASCII
- **Technique:** 100% command-line native, not emulated
- **Scale:** 10,000+ hours of development, 1,400 weapons/armors rendered in ASCII
- **Innovation:** Procedurally generated artwork in Black Edition
- **Philosophy:** ASCII + player imagination creates the world
- **UX Insight:** "Easier on the eyes - no flashing, small palette, little animation"

### Stone Story RPG
- **Style:** Smooth animated ASCII, surprisingly relaxing atmosphere
- **Innovation:** Player can edit AI code controlling character
- **Technique:** Subtractive animation (remove characters frame-by-frame)
- **Key Principle:** "Iteration is key" - refinement through repeated revision

### Cogmind
- **Style:** "Most advanced terminal interface ever" - retrofuturistic
- **Character Set:** Code Page 437 (255 glyphs)
- **Scale:** 600+ item illustrations at 12×12 glyph default
- **Philosophy:** "Art is always more interesting with stringent limitations"

### Dwarf Fortress
- **Style:** Maximum simulation depth, emergent storytelling
- **Scale:** Entire procedurally-generated worlds
- **Tradition:** @ for player, $ for treasure, D for dragon

---

## Technical Techniques

### Character Alphabets

**Basic Set:**
```
` ~ ! ^ ( ) - _ + = ; : " ' , . \ / | < > [ ] { }
```

**Extended Set (for consistency):**
```
´ ‾ ¡ · o O v V T L 7 U c C x X
```

**Box Drawing:**
```
─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
```

**Shading Blocks:**
```
░ ▒ ▓ █  (light → medium → dark → solid)
```

**Geometric:**
```
◆ ◇ ◈ ● ○ ◎ ★ ☆ ▲ ▼ ◄ ►
```

### Shading & Depth

| Technique | Characters | Effect |
|-----------|------------|--------|
| Anti-aliasing | `│ \ /` transitions | Smooths diagonal edges |
| Dithering | `. : ; ,` sparse | Tonal gradation |
| Shadows | `_ \` layered | Dimensional depth |
| Negative space | Strategic emptiness | Form and perspective |
| Gradient | `░▒▓█` progression | Density/darkness scale |

### Line Construction

```
Horizontal: ─ ═ - _ ~
Vertical:   │ ║ | !
Diagonal:   / \ ╱ ╲
Curves:     ( ) { } [ ]
Corners:    ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
```

### Font Considerations

- **Aspect Ratio:** 1:1 vs 1:2 (16:29)
- **Recommended:** Courier, Verdana, FixedSys, or terminal default
- **Key:** Mono-spaced fonts only
- **Width:** Keep under 80 characters for terminal compatibility

---

## Design Principles

### Abstraction Spectrum

```
HIGHLY ABSTRACT                              DETAILED
    │                                            │
    ▼                                            ▼
  Few chars                                Many chars
  Max imagination                          Suggestive detail
  Simple icons                             Complex scenes

  Example: @                    Example: Full character portrait
```

### The Roguelike Tradition

| Symbol | Meaning | Origin |
|--------|---------|--------|
| @ | Player ("where you're at") | Rogue |
| $ | Treasure/gold | Rogue |
| D | Dragon | Rogue |
| # | Wall | Universal |
| . | Floor | Universal |
| > | Stairs down | Universal |
| < | Stairs up | Universal |

### Composition Guidelines

1. **Establish silhouette first** - The overall shape should read clearly
2. **Add internal detail second** - Fill in after form is solid
3. **Use negative space intentionally** - Empty space is a design element
4. **Maintain consistent weight** - Similar density across pieces
5. **Test at actual render size** - Design for final display context

---

## Animation Techniques (Stone Story RPG)

### Subtractive Animation
Remove characters frame-by-frame to create motion illusion.

### Workflow
1. **References** - Gather visual inspiration
2. **Concept** - Rough idea/sketch
3. **Keyframe** - Major poses
4. **Size testing** - Verify dimensions work
5. **Animation planning** - Map movement
6. **Keyframes** - Create key moments
7. **Tweening** - Fill between keys
8. **Polish** - Refine details

---

## PatternForge Application

### Our Theme: Dark Fantasy / Cipher Crypts

**Mood Keywords:**
- Ancient
- Mysterious
- Cryptographic
- Shadowy
- Powerful
- Arcane

**Visual Motifs:**
- Locks and keys
- Ciphers and runes
- Crypts and vaults
- Crowns and thrones
- Gates and barriers
- Shadows and light

### Current Art Pieces (Enhanced)

| Piece | Technique Used |
|-------|----------------|
| CLI_BANNER | Gradient border (░▒▓), block letters, SCARAB boxes |
| CITADEL_LORD | Shading progression, diamond motifs, layered robes |
| GATEKEEPER | Geometric armor, cipher locks, ethereal head |
| VICTORY | Star/diamond formations, celebration framing |
| LOCK_TIER_1-6 | Progressive complexity, consistent style |

### Future Opportunities

1. **Animated encounters** - Subtle movement for bosses
2. **Procedural elements** - Generated variations on base art
3. **Color themes** - Gruvbox, SpecterOps palettes
4. **First-person perspective** - SanctuaryRPG style for key moments
5. **Symbolic language** - Consistent iconography for game elements

---

## Sources

- [SanctuaryRPG Classic](https://blackshellgames.itch.io/srpg)
- [Stone Story RPG ASCII Tutorial](https://stonestoryrpg.com/ascii_tutorial.html)
- [Cogmind ASCII Art Blog](https://www.gridsagegames.com/blog/2014/03/ascii-art/)
- [Best Roguelikes with ASCII Art](https://gamerant.com/best-roguelikes-ascii-art/)
- [Best Modern ASCII Games](https://www.thegamer.com/best-modern-ascii-games/)

---

*"ASCII art gives the viewer's imagination a starting point while leaving room for interpretation."*

— Fraz, The Pigment Alchemist
