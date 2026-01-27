#!/usr/bin/env python3
"""Generate title screen wireframe from canvas layout."""

from PIL import Image, ImageDraw, ImageFont

# Canvas size
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 35)
BORDER_COLOR = (139, 90, 43)
TEXT_COLOR = (235, 219, 178)
ACCENT_COLOR = (214, 93, 14)

# Positions from canvas (normalized to 800x600)
# Canvas origin was at y:300, so subtract 300 from all y values
CANVAS_ORIGIN_Y = 300

layout = {
    "splash_art": {"x": 40, "y": 350 - CANVAS_ORIGIN_Y, "width": 720, "height": 490},
    "title": {"x": 90, "y": 520 - CANVAS_ORIGIN_Y, "width": 300, "height": 50},
    "menu": {"x": 90, "y": 650 - CANVAS_ORIGIN_Y, "width": 200, "height": 140},
    "flavor": {"x": 400, "y": 700 - CANVAS_ORIGIN_Y, "width": 300, "height": 40},
}

# Create image
img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Fonts
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 28)
    font_medium = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
    font_small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
except:
    font_large = ImageFont.load_default()
    font_medium = font_large
    font_small = font_large

# === SPLASH ART ===
s = layout["splash_art"]
draw.rectangle(
    [s["x"], s["y"], s["x"] + s["width"], s["y"] + s["height"]],
    outline=BORDER_COLOR, width=2
)
# Corner accents
corner_len = 20
corners = [
    (s["x"], s["y"]),
    (s["x"] + s["width"], s["y"]),
    (s["x"], s["y"] + s["height"]),
    (s["x"] + s["width"], s["y"] + s["height"])
]
for cx, cy in corners:
    dx = corner_len if cx == s["x"] else -corner_len
    dy = corner_len if cy == s["y"] else -corner_len
    draw.line([(cx, cy), (cx + dx, cy)], fill=ACCENT_COLOR, width=2)
    draw.line([(cx, cy), (cx, cy + dy)], fill=ACCENT_COLOR, width=2)

# Placeholder text in splash
placeholder = "SPLASH ART"
bbox = draw.textbbox((0, 0), placeholder, font=font_medium)
px = s["x"] + (s["width"] - (bbox[2] - bbox[0])) // 2
py = s["y"] + s["height"] // 3
draw.text((px, py), placeholder, fill=(80, 80, 80), font=font_medium)

# === TITLE ===
t = layout["title"]
title_text = "THE DREAD CITADEL"
bbox = draw.textbbox((0, 0), title_text, font=font_large)
# Draw at specified position
draw.text((t["x"], t["y"]), title_text, fill=ACCENT_COLOR, font=font_large)
# Underline
title_width = bbox[2] - bbox[0]
draw.line([(t["x"], t["y"] + 35), (t["x"] + title_width, t["y"] + 35)], fill=BORDER_COLOR, width=1)

# === MENU ===
m = layout["menu"]
menu_items = ["[N] New Game", "[C] Continue", "[P] Profile", "[ESC] Quit"]
menu_spacing = 28
for i, item in enumerate(menu_items):
    draw.text((m["x"], m["y"] + i * menu_spacing), item, fill=TEXT_COLOR, font=font_medium)

# === FLAVOR ===
f = layout["flavor"]
flavor_text = '"The Circle awaits, Infiltrator."'
draw.text((f["x"], f["y"]), flavor_text, fill=(150, 150, 140), font=font_small)

# Save
output_path = "/Users/petermckernan/Projects/PatternForge/assets/images/review/needs_review/ui_mockup_title_v3.png"
img.save(output_path)
print(f"Saved: {output_path}")
