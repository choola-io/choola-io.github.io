"""Generate three images for the Choola site:
  - og.png            (1200x630) — Open Graph social preview
  - pdf-summarizer-canvas.png (1200x720) — empty editor canvas mock
  - pdf-summarizer-run.png    (1200x720) — four green nodes after a successful run

Uses the same fonts as the site (Cormorant Garamond, EB Garamond)
so the previews match the live design.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

SITE = Path("/home/ivan/choola-site/choola-io.github.io")
FONT_DIR = Path("/tmp")

# Palette — matches style.css :root vars
BG = (250, 250, 247)        # --bg
INK = (28, 28, 26)           # --ink
INK_SOFT = (85, 85, 85)      # --ink-soft
RULE = (216, 214, 207)       # --rule
LINK = (26, 77, 143)         # --link
CODE_BG = (243, 241, 234)    # --code-bg

# Node colors for the workflow run screenshot
NODE_GREEN_FILL = (232, 245, 233)
NODE_GREEN_BORDER = (76, 134, 86)
NODE_EMPTY_BORDER = (180, 178, 168)


def load_font(filename, size, weight=None):
    font = ImageFont.truetype(str(FONT_DIR / filename), size)
    if weight is not None:
        try:
            font.set_variation_by_axes([weight])
        except Exception:
            pass
    return font


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ---------- 1. og.png ----------

def make_og():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Subtle rule near the top edge for "letterhead" feel
    margin = 60
    d.rectangle([margin, margin, W - margin, margin + 1], fill=RULE)
    d.rectangle([margin, H - margin, W - margin, H - margin + 1], fill=RULE)

    # Title — .Choola in Cormorant Garamond medium, very large
    title_font = load_font("CormorantGaramond.ttf", 280, weight=500)
    title = ".Choola"
    tw, th = text_size(d, title, title_font)
    # Optical center slightly above geometric center
    d.text(((W - tw) / 2, H / 2 - th / 2 - 60), title, fill=INK, font=title_font)

    # Tagline — EB Garamond italic
    tag_font = load_font("EBGaramond-Italic.ttf", 38, weight=400)
    tag = "An automation programming framework for AI coding agents."
    twt, _ = text_size(d, tag, tag_font)
    d.text(((W - twt) / 2, H / 2 + 110), tag, fill=INK_SOFT, font=tag_font)

    # Footer — URL in EB Garamond regular
    foot_font = load_font("EBGaramond-Regular.ttf", 28, weight=400)
    foot = "choola.io  ·  github.com/igrosny/choola"
    fwt, _ = text_size(d, foot, foot_font)
    d.text(((W - fwt) / 2, H - margin - 50), foot, fill=INK_SOFT, font=foot_font)

    img.save(SITE / "og.png", "PNG", optimize=True)
    print("wrote", SITE / "og.png")


# ---------- 2. workflow canvas mocks ----------

def draw_canvas_background(d, W, H):
    """Dotted grid like a typical node editor."""
    dot = (220, 218, 210)
    step = 28
    r = 1
    for y in range(step, H, step):
        for x in range(step, W, step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=dot)


def draw_window_chrome(d, W, H):
    """Top toolbar + sidebar suggestion."""
    # Toolbar
    d.rectangle([0, 0, W, 56], fill=(248, 246, 240))
    d.line([0, 56, W, 56], fill=RULE)
    # ".Choola" mark in toolbar
    mark_font = load_font("CormorantGaramond.ttf", 30, weight=500)
    d.text((24, 14), ".Choola", fill=INK, font=mark_font)

    # Tabs to the right
    tab_font = load_font("EBGaramond-Regular.ttf", 18)
    for i, label in enumerate(["Workflows", "Database", "VectorDB", "Credentials"]):
        x = 240 + i * 130
        d.text((x, 19), label, fill=INK_SOFT, font=tab_font)

    # Left sidebar
    d.rectangle([0, 56, 240, H], fill=(252, 250, 246))
    d.line([240, 56, 240, H], fill=RULE)
    sb_font = load_font("EBGaramond-Regular.ttf", 18)
    d.text((24, 80), "WORKFLOWS", fill=INK_SOFT, font=sb_font)
    d.line([24, 108, 216, 108], fill=RULE)


def rounded_rect(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_node(d, cx, cy, label, sub, state="empty"):
    """A workflow node card."""
    w, h = 200, 78
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    if state == "green":
        fill = NODE_GREEN_FILL
        border = NODE_GREEN_BORDER
        bw = 2
    else:
        fill = (255, 254, 251)
        border = NODE_EMPTY_BORDER
        bw = 1
    rounded_rect(d, box, 8, fill, outline=border, width=bw)

    label_font = load_font("EBGaramond-Regular.ttf", 20, weight=500)
    sub_font = load_font("EBGaramond-Italic.ttf", 15)
    lw, lh = text_size(d, label, label_font)
    d.text((cx - lw / 2, cy - 26), label, fill=INK, font=label_font)
    sw, sh = text_size(d, sub, sub_font)
    d.text((cx - sw / 2, cy + 2), sub, fill=INK_SOFT, font=sub_font)

    if state == "green":
        # Status dot
        d.ellipse([box[2] - 18, box[1] + 8, box[2] - 8, box[1] + 18],
                  fill=NODE_GREEN_BORDER)


def draw_arrow(d, x1, y1, x2, y2, color=(150, 148, 138)):
    d.line([x1, y1, x2, y2], fill=color, width=2)
    # Arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    s = 9
    p1 = (x2 - s * math.cos(angle - math.pi / 7),
          y2 - s * math.sin(angle - math.pi / 7))
    p2 = (x2 - s * math.cos(angle + math.pi / 7),
          y2 - s * math.sin(angle + math.pi / 7))
    d.polygon([(x2, y2), p1, p2], fill=color)


def make_empty_canvas():
    W, H = 1200, 720
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_canvas_background(d, W, H)
    draw_window_chrome(d, W, H)

    # Center placeholder
    hint_title = load_font("CormorantGaramond.ttf", 48, weight=500)
    hint_body = load_font("EBGaramond-Italic.ttf", 22)
    title = "No workflows yet"
    tw, th = text_size(d, title, hint_title)
    cx = (240 + W) / 2
    cy = H / 2
    d.text((cx - tw / 2, cy - 50), title, fill=INK_SOFT, font=hint_title)
    body = "Run  choola create my-workflow  or describe one to Claude with  /workflow"
    bw, bh = text_size(d, body, hint_body)
    d.text((cx - bw / 2, cy + 10), body, fill=INK_SOFT, font=hint_body)

    img.save(SITE / "workflows" / "images" / "pdf-summarizer-canvas.png",
             "PNG", optimize=True)
    print("wrote", SITE / "workflows" / "images" / "pdf-summarizer-canvas.png")


def make_run_canvas():
    W, H = 1200, 720
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_canvas_background(d, W, H)
    draw_window_chrome(d, W, H)

    # Workflow name in sidebar
    sb_active = load_font("EBGaramond-Regular.ttf", 19, weight=500)
    d.rectangle([8, 120, 232, 152], fill=(238, 234, 222))
    d.text((24, 124), "pdf-summary", fill=INK, font=sb_active)

    # Four nodes in a row across the canvas area
    canvas_left = 240
    canvas_right = W
    canvas_top = 56
    cx_mid = (canvas_left + canvas_right) / 2
    cy = (canvas_top + H) / 2 - 20

    nodes = [
        ("FormTrigger", "form_trigger"),
        ("ExtractText", "extract_text"),
        ("LLM", "summarize"),
        ("Gmail", "send_email"),
    ]
    n = len(nodes)
    spacing = 220
    start_x = cx_mid - spacing * (n - 1) / 2

    positions = []
    for i, (label, sub) in enumerate(nodes):
        x = start_x + i * spacing
        positions.append(x)
        draw_node(d, x, cy, label, sub, state="green")

    # Arrows between nodes
    for i in range(n - 1):
        x1 = positions[i] + 100
        x2 = positions[i + 1] - 100
        draw_arrow(d, x1, cy, x2, cy)

    # Run status bar at the top of canvas
    status_font = load_font("EBGaramond-Regular.ttf", 18, weight=500)
    sub_font = load_font("EBGaramond-Italic.ttf", 16)
    d.rectangle([canvas_left + 32, 88, canvas_left + 360, 130],
                fill=NODE_GREEN_FILL, outline=NODE_GREEN_BORDER, width=1)
    d.ellipse([canvas_left + 46, 102, canvas_left + 60, 116],
              fill=NODE_GREEN_BORDER)
    d.text((canvas_left + 72, 100), "Run complete  ·  9.2s  ·  3,140 tokens",
           fill=INK, font=status_font)

    # Tiny per-node duration captions
    cap_font = load_font("EBGaramond-Italic.ttf", 14)
    durations = ["0.0s", "0.4s", "8.7s", "0.1s"]
    for x, dur in zip(positions, durations):
        dw, _ = text_size(d, dur, cap_font)
        d.text((x - dw / 2, cy + 60), dur, fill=INK_SOFT, font=cap_font)

    img.save(SITE / "workflows" / "images" / "pdf-summarizer-run.png",
             "PNG", optimize=True)
    print("wrote", SITE / "workflows" / "images" / "pdf-summarizer-run.png")


if __name__ == "__main__":
    make_og()
    make_empty_canvas()
    make_run_canvas()
