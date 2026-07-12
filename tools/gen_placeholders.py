"""Generate tasteful abstract 'design work' placeholders for the demo gallery.

Swiss/editorial-style compositions so the layout can be judged with real weight
behind it instead of grey boxes. Replaced by the client's real work later.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "site", "assets", "img")
os.makedirs(OUT, exist_ok=True)

F_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_NARROW = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

PALETTES = [
    ("#F4F1EA", "#12100E", "#C8553D"),
    ("#0E1116", "#F2F2F0", "#E4B363"),
    ("#EDEAE4", "#1B2A41", "#324A5F"),
    ("#F7F3EF", "#2B2118", "#8A9A5B"),
    ("#1A1A1A", "#EFEFEF", "#D64550"),
    ("#E8E6E1", "#111111", "#3D5A80"),
    ("#FBF7F0", "#22333B", "#A44A3F"),
    ("#101820", "#F2AA4C", "#F2F2F2"),
    ("#EFE9E1", "#4A4A48", "#B08968"),
]


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def grain(im, amount=6):
    px = im.load()
    w, h = im.size
    for _ in range((w * h) // 40):
        x, y = random.randrange(w), random.randrange(h)
        r, g, b = px[x, y]
        d = random.randint(-amount, amount)
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return im


def compose(idx, w, h, title, kicker):
    bg, fg, accent = (hx(c) for c in PALETTES[idx % len(PALETTES)])
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im, "RGBA")
    m = int(w * 0.09)
    style = idx % 5

    if style == 0:  # stacked bars
        for i in range(6):
            y = int(h * 0.22) + i * int(h * 0.09)
            bw = int(w * (0.82 - i * 0.11))
            d.rectangle([m, y, m + bw, y + int(h * 0.055)], fill=accent if i % 2 else fg)
    elif style == 1:  # circle over rule
        r = int(min(w, h) * 0.28)
        cx, cy = w // 2, int(h * 0.44)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        d.rectangle([m, cy - 6, w - m, cy + 6], fill=fg)
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=bg)
    elif style == 2:  # modular grid
        cols, rows = 4, 5
        cw = (w - 2 * m) // cols
        ch = int(h * 0.52) // rows
        top = int(h * 0.2)
        for r_ in range(rows):
            for c_ in range(cols):
                if random.random() < 0.45:
                    continue
                x0 = m + c_ * cw
                y0 = top + r_ * ch
                col = accent if (r_ + c_) % 3 == 0 else fg
                if random.random() < 0.3:
                    d.ellipse([x0 + 6, y0 + 6, x0 + cw - 12, y0 + ch - 12], fill=col)
                else:
                    d.rectangle([x0 + 6, y0 + 6, x0 + cw - 12, y0 + ch - 12], fill=col)
    elif style == 3:  # diagonal fields
        d.polygon([(0, int(h * 0.30)), (w, int(h * 0.10)), (w, int(h * 0.60)), (0, int(h * 0.80))], fill=accent)
        d.polygon([(0, int(h * 0.62)), (w, int(h * 0.42)), (w, int(h * 0.55)), (0, int(h * 0.75))], fill=fg)
    else:  # concentric arcs
        cx, cy = int(w * 0.5), int(h * 0.45)
        for i in range(7, 0, -1):
            rr = int(min(w, h) * 0.05 * i)
            col = accent if i % 2 else fg
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=col, width=int(w * 0.018))

    f_kick = ImageFont.truetype(F_MONO, int(w * 0.026))
    f_title = ImageFont.truetype(F_NARROW, int(w * 0.085))
    d.text((m, int(h * 0.09)), kicker.upper(), font=f_kick, fill=fg)
    d.text((m, h - m - int(w * 0.10)), title.upper(), font=f_title, fill=fg)
    d.rectangle([m, h - m - int(w * 0.125), m + int(w * 0.14), h - m - int(w * 0.118)], fill=accent)
    return grain(im)


PROJECTS = [
    ("Meridian Coffee", "Brand Identity", 1600, 2000),
    ("Northline Type", "Typeface Design", 1600, 1200),
    ("Kite Festival", "Poster Series", 1600, 2000),
    ("Studio Alba", "Visual Identity", 1600, 1600),
    ("Field Notes", "Editorial Design", 1600, 1200),
    ("Halcyon Records", "Album Artwork", 1600, 1600),
    ("Terra Botanics", "Packaging", 1600, 2000),
    ("Civic Museum", "Wayfinding", 1600, 1200),
    ("Ember & Ash", "Brand Identity", 1600, 1600),
]

random.seed(7)
manifest = []
for i, (title, kicker, w, h) in enumerate(PROJECTS, start=1):
    im = compose(i - 1, w, h, title, kicker)
    slug = title.lower().replace(" & ", "-").replace(" ", "-")
    # @2x master + 1x, both WebP (retina-ready srcset)
    im.save(f"{OUT}/{slug}@2x.webp", "WEBP", quality=82, method=6)
    im.resize((w // 2, h // 2), Image.LANCZOS).save(f"{OUT}/{slug}.webp", "WEBP", quality=84, method=6)
    im.resize((w // 4, h // 4), Image.LANCZOS).save(f"{OUT}/{slug}-thumb.jpg", "JPEG", quality=80, optimize=True)
    manifest.append((slug, title, kicker, w, h))
    print(slug, w, h)

# Portrait for the bio block
bio = compose(3, 1200, 1500, "Studio", "Portrait")
bio.save(f"{OUT}/portrait@2x.webp", "WEBP", quality=82, method=6)
bio.resize((600, 750), Image.LANCZOS).save(f"{OUT}/portrait.webp", "WEBP", quality=84, method=6)
print("done", len(manifest))
