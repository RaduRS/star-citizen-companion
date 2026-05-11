"""Generate the tray/app icon: a Star Citizen HUD-style targeting reticle on
deep space.

One-shot — run when the icon needs to be regenerated. Output is committed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SIZE = 256  # render large, Qt scales down nicely
OUT = Path(__file__).resolve().parent.parent / "src" / "sc_companion" / "data" / "icon.png"

# CIG/Star Citizen palette: deep space + amber HUD glow + cyan accent
SPACE_TOP = (5, 8, 18, 255)
SPACE_BOTTOM = (15, 22, 38, 255)
RETICLE_AMBER = (255, 168, 38, 255)
RETICLE_CYAN = (90, 220, 255, 255)
STAR = (220, 230, 255, 255)


def vertical_gradient(size: int, top: tuple, bottom: tuple) -> Image.Image:
    img = Image.new("RGBA", (size, size), top)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        px_color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4))
        for x in range(size):
            px[x, y] = px_color
    return img


# Base: gradient inside a rounded square mask
base = vertical_gradient(SIZE, SPACE_TOP, SPACE_BOTTOM)
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    (0, 0, SIZE - 1, SIZE - 1), radius=46, fill=255
)
out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
out.paste(base, mask=mask)

draw = ImageDraw.Draw(out)

# Sparse star field
stars = [
    (38, 52, 1), (60, 30, 2), (200, 44, 1), (224, 90, 2),
    (28, 150, 1), (52, 198, 2), (216, 200, 1), (190, 232, 1),
    (122, 22, 1), (138, 232, 2), (12, 110, 1), (244, 140, 1),
]
for x, y, r in stars:
    draw.ellipse((x - r, y - r, x + r, y + r), fill=STAR)

# Reticle geometry — centered, big enough to dominate
cx, cy = SIZE // 2, SIZE // 2
R_OUTER = 78
R_MID = 56
R_INNER = 18

# Outer brackets (4 arcs at corners, suggesting target lock)
bracket_pad = 14
for start, end in [(40, 70), (110, 140), (220, 250), (290, 320)]:
    draw.arc(
        (cx - R_OUTER - bracket_pad, cy - R_OUTER - bracket_pad,
         cx + R_OUTER + bracket_pad, cy + R_OUTER + bracket_pad),
        start=start, end=end, fill=RETICLE_AMBER, width=4,
    )

# Mid ring (full)
draw.ellipse(
    (cx - R_MID, cy - R_MID, cx + R_MID, cy + R_MID),
    outline=RETICLE_AMBER, width=3,
)

# Crosshair — gaps near the centre so the inner pip stays clean
gap = R_INNER + 8
arm = R_OUTER + bracket_pad - 6
for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    draw.line(
        (cx + dx * gap, cy + dy * gap, cx + dx * arm, cy + dy * arm),
        fill=RETICLE_CYAN, width=3,
    )

# Inner pip
draw.ellipse(
    (cx - R_INNER, cy - R_INNER, cx + R_INNER, cy + R_INNER),
    outline=RETICLE_CYAN, width=3,
)
draw.ellipse(
    (cx - 4, cy - 4, cx + 4, cy + 4), fill=RETICLE_CYAN,
)

# Soft glow pass: blur a copy of the reticle layer and composite under
glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_layer)
glow_draw.ellipse(
    (cx - R_MID, cy - R_MID, cx + R_MID, cy + R_MID),
    outline=(*RETICLE_AMBER[:3], 140), width=8,
)
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=8))
out = Image.alpha_composite(out, glow_layer)

# Re-draw the sharp reticle on top of the glow so edges stay crisp
draw = ImageDraw.Draw(out)
for start, end in [(40, 70), (110, 140), (220, 250), (290, 320)]:
    draw.arc(
        (cx - R_OUTER - bracket_pad, cy - R_OUTER - bracket_pad,
         cx + R_OUTER + bracket_pad, cy + R_OUTER + bracket_pad),
        start=start, end=end, fill=RETICLE_AMBER, width=4,
    )
draw.ellipse(
    (cx - R_MID, cy - R_MID, cx + R_MID, cy + R_MID),
    outline=RETICLE_AMBER, width=3,
)
for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    draw.line(
        (cx + dx * gap, cy + dy * gap, cx + dx * arm, cy + dy * arm),
        fill=RETICLE_CYAN, width=3,
    )
draw.ellipse(
    (cx - R_INNER, cy - R_INNER, cx + R_INNER, cy + R_INNER),
    outline=RETICLE_CYAN, width=3,
)
draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=RETICLE_CYAN)

# Re-mask to keep the rounded-square silhouette (in case glow leaked)
final = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
final.paste(out, mask=mask)
out = final

OUT.parent.mkdir(parents=True, exist_ok=True)
out.save(OUT, format="PNG")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")

ICO_OUT = OUT.with_suffix(".ico")
out.save(ICO_OUT, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(f"wrote {ICO_OUT} ({ICO_OUT.stat().st_size} bytes)")
