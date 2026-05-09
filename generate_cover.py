#!/usr/bin/env python3
"""
generate_cover.py — Gita Guru · Reel Cover Image Generator
Generates a 1080x1920 PNG cover image for each reel, uploaded via cover_url param.

Visual style mirrors generate_video.py (same palette, same fonts):
  - Dark BG with warm edge glow
  - Large OM symbol (gold, central)
  - Hook pain-point text (saffron, bold)  ← stops the scroll in profile grid
  - Verse reference + first 2 Sanskrit lines (preview)
  - GITA GURU branding top/bottom

INSTAGRAM API:
  pass cover_url = <public URL to this PNG> when creating the media container.
  cover_url takes precedence over thumb_offset.

USAGE:
  python generate_cover.py        # reads progress.json, writes cover.png
  # then upload cover.png to your public host and set COVER_URL env var before upload.py
"""

import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1920

# Instagram feed crops to the centre 1080×1080 square.
# Key content MUST live within these y bounds to avoid being cut on the grid.
CROP_TOP = (H - W) // 2  # 420 px from top
CROP_BOT = CROP_TOP + W  # 1500 px from top
CROP_PAD = 30  # inner breathing room inside crop zone

# ── Palette (matches generate_video.py exactly) ───────────────────────────────
BG = (8, 6, 13)  # #08060D
WARM = (26, 8, 0)  # #1A0800
GOLD = (201, 160, 63)  # #C9A03F
GOLD_LT = (237, 208, 122)  # #EDD07A
WHITE = (242, 239, 232)  # #F2EFE8
SAFFRON = (224, 92, 10)  # #E05C0A
MUTED = (122, 130, 152)  # #7A8298
DIVCLR = (176, 144, 64)  # #B09040

# ── Hook map (mirrors generate_video.py) ─────────────────────────────────────
HOOK_MAP = {
    1: (
        "Feeling confused and\noverwhelmed?",
        "Krishna answered this\n5,000 years ago.",
    ),
    2: ("Feeling stuck and\nnot knowing why?", "The Gita has your answer."),
    3: (
        "Doing everything right\nbut getting no results?",
        "This verse will shift\nyour perspective.",
    ),
    4: ("Doubting yourself\nand your path?", "Read this slowly."),
    5: ("Struggling to stay\ncalm under pressure?", "Ancient wisdom for modern life."),
    6: (
        "Anxious mind that\nwon't stop racing?",
        "Krishna taught the cure\n5,000 years ago.",
    ),
    7: ("Searching for meaning\nin what you do?", "This verse changes everything."),
    8: ("Afraid of what\ncomes next in life?", "The Gita speaks to this directly."),
    9: ("Feeling unseen and\nunappreciated?", "This is for you."),
    10: ("Want to do great things\nbut feel small?", "Read this before you give up."),
    11: ("Overwhelmed by life's\nbig picture?", "There is a bigger force at work."),
    12: ("Hard to love people\nwho hurt you?", "The Gita's answer is profound."),
    13: ("Not sure who you\nreally are?", "This verse will ground you."),
    14: ("Why do you keep repeating\nthe same patterns?", "The Gita explains it."),
    15: (
        "Distracted by every\nshiny thing around you?",
        "This one verse cuts\nthrough the noise.",
    ),
    16: ("Surrounded by toxic\nenergy and people?", "Krishna warned us about this."),
    17: ("Not sure if your\nfaith is strong enough?", "This verse will reassure you."),
    18: ("Struggling to let go\nand just do the work?", "BG 18 holds the answer."),
    "DEFAULT": (
        "Feeling lost in\nthe noise of life?",
        "The Gita has always\nhad the answer.",
    ),
}


def _get_hook(chapter: int) -> tuple:
    return HOOK_MAP.get(chapter, HOOK_MAP["DEFAULT"])


# ── Font loading ──────────────────────────────────────────────────────────────
def _fc_match(family: str) -> str | None:
    """Use fc-match (Linux/macOS) to resolve a font family to a file path."""
    try:
        r = subprocess.run(
            ["fc-match", "--format=%{file}", family],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None


def _search_font(candidates: list[str]) -> str | None:
    """Walk common font directories looking for candidate filenames."""
    roots = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        "C:/Windows/Fonts",
        os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
        os.path.expanduser("~/Library/Fonts"),  # macOS
        "/System/Library/Fonts",
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for c in candidates:
                if c in filenames:
                    return os.path.join(dirpath, c)
    return None


def _load_font(
    size: int, bold: bool = False, devanagari: bool = False
) -> ImageFont.FreeTypeFont:
    path = None

    if devanagari:
        if not sys.platform.startswith("win"):
            path = _fc_match("Noto Sans Devanagari")
        if not path:
            path = _search_font(
                [
                    "NotoSansDevanagari-Regular.ttf",
                    "NotoSansDevanagari[wdth,wght].ttf",
                    "NotoSansDevanagari.ttf",
                ]
            )
    elif bold:
        if not sys.platform.startswith("win"):
            path = _fc_match("Noto Sans:bold")
        if not path:
            # Try Noto Sans Bold first, then fall back to system bold fonts
            path = _search_font(
                [
                    "NotoSans-Bold.ttf",
                    "NotoSans[wdth,wght].ttf",
                    "NotoSans-SemiBold.ttf",
                    "NotoSans.ttf",
                    # Windows system fonts with good Unicode coverage
                    "arialbd.ttf",  # Arial Bold
                    "segoeuib.ttf",  # Segoe UI Bold
                    "calibrib.ttf",  # Calibri Bold
                ]
            )
    else:
        if not sys.platform.startswith("win"):
            path = _fc_match("Noto Sans")
        if not path:
            path = _search_font(
                [
                    "NotoSans-Regular.ttf",
                    "NotoSans[wdth,wght].ttf",
                    "NotoSans.ttf",
                    # Windows system fonts with good Unicode coverage
                    "arial.ttf",  # Arial
                    "segoeui.ttf",  # Segoe UI
                    "calibri.ttf",  # Calibri
                ]
            )

    if path and os.path.isfile(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    # Last-resort: Pillow built-in (no anti-aliasing, fixed size)
    print(
        f"[cover] WARNING: could not find a suitable font — using PIL default (size {size})"
    )
    return ImageFont.load_default()


# ── Background ─────────────────────────────────────────────────────────────────
def _make_background() -> Image.Image:
    """Near-black background with warm ambient glow at top and bottom edges."""
    arr = np.full((H, W, 3), BG, dtype=np.uint8)
    glow_px = 320
    for y in range(glow_px):
        t = ((glow_px - y) / glow_px) ** 2  # quadratic, strongest at edge
        arr[y] = np.clip(
            np.array(BG) + t * (np.array(WARM) - np.array(BG)), 0, 255
        ).astype(np.uint8)
    for y in range(H - glow_px, H):
        t = ((y - (H - glow_px)) / glow_px) ** 2
        arr[y] = np.clip(
            np.array(BG) + t * (np.array(WARM) - np.array(BG)), 0, 255
        ).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


# ── Draw helpers ──────────────────────────────────────────────────────────────
def _text_bbox(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont
) -> tuple:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1], bb[0], bb[1]  # w, h, x_off, y_off


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: tuple,
    alpha: int = 255,
) -> int:
    """Draw text centred on x-axis at y. Returns the bottom y of the rendered text."""
    w, h, x_off, y_off = _text_bbox(draw, text, font)
    x = (W - w) // 2 - x_off
    fill = (*color, alpha)
    draw.text((x, y - y_off), text, font=font, fill=fill)
    return y + h


def _draw_multiline_centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: tuple,
    gap: int = 16,
    alpha: int = 255,
) -> int:
    """Draw multi-line text (split on \\n) centred. Returns bottom y."""
    for line in text.split("\n"):
        y = _draw_centered(draw, y, line, font, color, alpha)
        y += gap
    return y - gap  # undo last extra gap


def _draw_divider(
    draw: ImageDraw.ImageDraw,
    y: int,
    width: int = 820,
    color: tuple = DIVCLR,
    alpha: int = 160,
) -> None:
    """Centred divider: line ◆ line."""
    cx = W // 2
    half = width // 2
    dot_r = 6
    gap = 18
    fill = (*color, alpha)
    draw.line([(cx - half, y), (cx - gap, y)], fill=fill, width=2)
    draw.line([(cx + gap, y), (cx + half, y)], fill=fill, width=2)
    draw.ellipse([(cx - dot_r, y - dot_r), (cx + dot_r, y + dot_r)], fill=fill)


# ── Data helpers ──────────────────────────────────────────────────────────────
def _load_shloka() -> tuple:
    with open("progress.json", encoding="utf-8") as f:
        idx = json.load(f)["last_posted_index"] + 1
    with open("shlokas.json", encoding="utf-8") as f:
        shlokas = json.load(f)
    if idx >= len(shlokas):
        print("All shlokas posted!")
        sys.exit(0)
    return shlokas[idx], idx


# ── Cover layout ───────────────────────────────────────────────────────────────
#
# Instagram feed grid shows only the centre 1080×1080 square (y=420–1500).
# ALL visible content is placed within CROP_TOP+PAD … CROP_BOT-PAD (y≈450–1470)
# so nothing is half-cut on the grid.  The top/bottom strips of the full
# 1920px image are ambient glow only — they show in the reel but not the grid.
#
#  y= 450  G I T A  G U R U  (brand, GOLD, 48px bold)       ← top of crop zone
#  y= 516  brand underline divider
#  y= 548  OM symbol  ॐ  (GOLD_LT, 200px Devanagari)
#  y= 820  wide divider
#  y= 858  Hook line 1  (SAFFRON, 72px bold)  — varies per chapter
#  y=  …   Hook line 2  (MUTED, 44px)
#  y=  …   divider
#  y=  …   Bhagavad Gita · Chapter X, Verse Y  (MUTED, 34px)
#  y=  …   Sanskrit line 1  (GOLD, 46px Devanagari)  — first line only
#  y=  …   ◆  ◆  ◆  ornament                            ← within crop zone
#  y=1840  @gita_guru_app · follow for daily wisdom     ← below crop (reel only)
#
def generate_cover(shloka: dict, output_path: str = "cover.png") -> str:
    img = _make_background().convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Pre-load fonts (slightly smaller than video to fit everything in crop zone)
    f_brand = _load_font(48, bold=True)
    f_om = _load_font(200, devanagari=True)
    f_hook1 = _load_font(72, bold=True)
    f_hook2 = _load_font(44)
    f_ref = _load_font(34)
    f_sans = _load_font(46, devanagari=True)
    f_orn = _load_font(22)
    f_wm = _load_font(30)

    hook_l1, hook_l2 = _get_hook(shloka["chapter"])

    # ── Brand header — top of crop zone ───────────────────────────────────────
    _draw_centered(draw, CROP_TOP + CROP_PAD, "G I T A  G U R U", f_brand, GOLD)
    _draw_divider(draw, CROP_TOP + CROP_PAD + 66, width=480, color=GOLD, alpha=130)

    # ── OM symbol ─────────────────────────────────────────────────────────────
    # At 200px font the OM glyph is ~260px tall; placed just below brand line.
    _draw_centered(draw, CROP_TOP + CROP_PAD + 98, "ॐ", f_om, GOLD_LT)

    # ── Divider below OM ──────────────────────────────────────────────────────
    # OM bottom ≈ CROP_TOP + PAD + 98 + 260 = 806 → divider at 820
    _draw_divider(draw, 820, width=840, alpha=165)

    # ── Hook text ─────────────────────────────────────────────────────────────
    y = 858
    y = _draw_multiline_centered(draw, y, hook_l1, f_hook1, SAFFRON, gap=12)
    y += 36
    y = _draw_multiline_centered(draw, y, hook_l2, f_hook2, MUTED, gap=10)

    # ── Divider ───────────────────────────────────────────────────────────────
    y += 46
    _draw_divider(draw, y, width=840, alpha=165)
    y += 54

    # ── Verse reference ───────────────────────────────────────────────────────
    ref = f"Bhagavad Gita  ·  Chapter {shloka['chapter']}, Verse {shloka['verse']}"
    y = _draw_centered(draw, y, ref, f_ref, MUTED)
    y += 38

    # ── Sanskrit first line — teaser (single line to stay within crop zone) ───
    sans_lines = [l.strip() for l in shloka["sanskrit"].split("\n") if l.strip()]
    if sans_lines:
        y = _draw_centered(draw, y, sans_lines[0], f_sans, GOLD)
        y += 28

    # ── Ornament — last element inside crop zone ───────────────────────────────
    _draw_centered(draw, y, "◆  ◆  ◆", f_orn, DIVCLR, alpha=160)

    # ── Bottom watermark — below crop zone, visible in reel only ──────────────
    _draw_centered(
        draw,
        H - 88,
        "@gita_guru_app  ·  follow for daily wisdom",
        f_wm,
        MUTED,
        alpha=180,
    )

    # ── Composite and save ────────────────────────────────────────────────────
    result = Image.alpha_composite(img, layer).convert("RGB")
    result.save(output_path, "PNG")
    print(f"✅ Cover generated: {output_path}")
    return output_path


if __name__ == "__main__":
    shloka, _ = _load_shloka()
    generate_cover(shloka)
