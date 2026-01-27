#!/usr/bin/env python3
"""Generate centered title screen wireframe."""

from PIL import Image, ImageDraw, ImageFont

# Canvas size (match game window)
WIDTH, HEIGHT = 800, 600
BG_COLOR = (30, 30, 35)
BORDER_COLOR = (139, 90, 43)  # Gruvbox orange-brown
TEXT_COLOR = (235, 219, 178)  # Gruvbox fg
ACCENT_COLOR = (214, 93, 14)  # Gruvbox orange

# Create image
img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Try to use a monospace font, fall back to default
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 28)
    font_medium = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
    font_small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
except:
    font_large = ImageFont.load_default()
    font_medium = font_large
    font_small = font_large

# === SPLASH ART PLACEHOLDER (large, centered) ===
art_width, art_height = 500, 280
art_x = (WIDTH - art_width) // 2
art_y = 40

# Draw art frame
draw.rectangle(
    [art_x, art_y, art_x + art_width, art_y + art_height],
    outline=BORDER_COLOR, width=2
)
# Corner accents
corner_len = 15
# Top-left
draw.line([(art_x, art_y), (art_x + corner_len, art_y)], fill=ACCENT_COLOR, width=2)
draw.line([(art_x, art_y), (art_x, art_y + corner_len)], fill=ACCENT_COLOR, width=2)
# Top-right
draw.line([(art_x + art_width, art_y), (art_x + art_width - corner_len, art_y)], fill=ACCENT_COLOR, width=2)
draw.line([(art_x + art_width, art_y), (art_x + art_width, art_y + corner_len)], fill=ACCENT_COLOR, width=2)
# Bottom-left
draw.line([(art_x, art_y + art_height), (art_x + corner_len, art_y + art_height)], fill=ACCENT_COLOR, width=2)
draw.line([(art_x, art_y + art_height), (art_x, art_y + art_height - corner_len)], fill=ACCENT_COLOR, width=2)
# Bottom-right
draw.line([(art_x + art_width, art_y + art_height), (art_x + art_width - corner_len, art_y + art_height)], fill=ACCENT_COLOR, width=2)
draw.line([(art_x + art_width, art_y + art_height), (art_x + art_width, art_y + art_height - corner_len)], fill=ACCENT_COLOR, width=2)

# Placeholder text
placeholder_text = "SPLASH ART"
placeholder_sub = "Dread Citadel"
bbox1 = draw.textbbox((0, 0), placeholder_text, font=font_medium)
bbox2 = draw.textbbox((0, 0), placeholder_sub, font=font_small)
draw.text(
    (art_x + (art_width - (bbox1[2] - bbox1[0])) // 2, art_y + art_height // 2 - 20),
    placeholder_text, fill=(100, 100, 100), font=font_medium
)
draw.text(
    (art_x + (art_width - (bbox2[2] - bbox2[0])) // 2, art_y + art_height // 2 + 10),
    placeholder_sub, fill=(100, 100, 100), font=font_small
)

# === TITLE (centered below art) ===
title_text = "THE DREAD CITADEL"
title_y = art_y + art_height + 30
bbox = draw.textbbox((0, 0), title_text, font=font_large)
title_width = bbox[2] - bbox[0]
draw.text(
    ((WIDTH - title_width) // 2, title_y),
    title_text, fill=ACCENT_COLOR, font=font_large
)
# Underline
line_y = title_y + 35
line_half = title_width // 2 + 20
draw.line([(WIDTH // 2 - line_half, line_y), (WIDTH // 2 + line_half, line_y)], fill=BORDER_COLOR, width=1)

# === MENU (centered) ===
menu_items = [
    "[N] New Game",
    "[C] Continue",
    "[P] Profile",
    "[ESC] Quit"
]
menu_start_y = title_y + 60
menu_spacing = 28

for i, item in enumerate(menu_items):
    bbox = draw.textbbox((0, 0), item, font=font_medium)
    item_width = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - item_width) // 2, menu_start_y + i * menu_spacing),
        item, fill=TEXT_COLOR, font=font_medium
    )

# === FLAVOR TEXT (centered at bottom) ===
flavor_text = '"The Circle awaits, Infiltrator."'
flavor_y = HEIGHT - 60
bbox = draw.textbbox((0, 0), flavor_text, font=font_small)
flavor_width = bbox[2] - bbox[0]
draw.text(
    ((WIDTH - flavor_width) // 2, flavor_y),
    flavor_text, fill=(150, 150, 140), font=font_small
)

# Save
output_path = "/Users/petermckernan/Projects/PatternForge/assets/images/review/needs_review/ui_mockup_title_v2.png"
img.save(output_path)
print(f"Saved: {output_path}")
