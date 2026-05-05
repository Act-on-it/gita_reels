#!/usr/bin/env python3
"""
generate_video_v13.py  —  Gita Guru · Daily Shloka Reel  v13 (Professional Redesign)
Instagram-optimised portrait (1080×1920 @ 30fps) Manim video.

CONFIRMED runtime frame dimensions (manim -qh --resolution 1080,1920):
  frame_width  = 14.222 units   x ∈ [-7.11,  7.11]
  frame_height = 25.284 units   y ∈ [-12.64, 12.64]
  pixels_per_unit = 75.9

Instagram Reels safe area (clear of account / button UI overlays):
  top safe:    y < 9.3  (≈250 px from top)
  bottom safe: y > -8.0 (≈350 px from bottom)

All elements are placed with explicit y positions so content
fills the portrait frame naturally top-to-bottom.
"""

import json, os, sys
from manim import *

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_NAME = "shloka_video"
_STEM       = os.path.splitext(os.path.basename(__file__))[0]   # e.g. "generate_video_v13"
RENDER_DIR  = f"media/videos/{_STEM}/1920p30"
APP_ICON_PATH = "app_icon.png"

# Confirmed runtime frame constants
FW    = 14.222   # frame width in units
FH    = 25.284   # frame height in units  (= FW * 1920/1080)
PPU   = 75.9     # pixels per unit

# Key y positions (all within safe zone)
HUD_TOP_Y   =  9.5    # brand bar  (~8% from top)
HUD_BOT_Y   =  -8.5    # watermark  (~87% from top)

# ── Colour palette ─────────────────────────────────────────────────────────────
BG      = "#08060D"   # near-black with warm maroon undertone
WARM    = "#1A0800"   # deep warm brown (ambient gradient tint)
GOLD    = "#C9A03F"   # rich warm gold  (accents)
GOLD_LT = "#EDD07A"   # bright gold     (OM symbol)
WHITE   = "#F2EFE8"   # warm off-white  (English body)
SAFFRON = "#E05C0A"   # deep saffron    (headers, CTA)
MUTED   = "#7A8298"   # slate grey      (secondary, watermark)
DIVCLR  = "#B09040"   # mid-warm gold   (dividers)

FONT     = "Segoe UI"            # widely installed on Windows, clean
FONT_DEV = "Noto Sans Devanagari"  # confirmed present

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_shloka():
    with open("progress.json", encoding="utf-8") as f:
        idx = json.load(f)["last_posted_index"] + 1
    with open("shlokas.json", encoding="utf-8") as f:
        shlokas = json.load(f)
    if idx >= len(shlokas):
        print("All shlokas posted!")
        sys.exit(0)
    return shlokas[idx], idx

def update_progress(idx: int):
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump({"last_posted_index": idx}, f, indent=2)

# ── Shared design helpers ─────────────────────────────────────────────────────
def make_divider(width: float = 10.0, color=DIVCLR,
                 opacity: float = 0.80, stroke_w: float = 1.5) -> VGroup:
    """Horizontal rule with small diamond accent in the centre."""
    hw = width / 2 - 0.22
    left  = Line(LEFT * hw, ORIGIN, stroke_width=stroke_w, color=color)
    right = Line(ORIGIN, RIGHT * hw, stroke_width=stroke_w, color=color)
    dot   = Dot(radius=0.07, color=color)
    return VGroup(left, dot, right).set_opacity(opacity)


def make_ambient_glow() -> VGroup:
    """Subtle warm gradient panels at the very top and bottom of the frame
    to soften the pure-black edges and give visual depth."""
    top = Rectangle(width=FW, height=2.5,
                    fill_color=[WARM, BG], fill_opacity=1.0, stroke_width=0)
    top.set_sheen_direction(DOWN)
    top.move_to(UP * (FH / 2 - 1.25))    # glued to top edge

    bot = Rectangle(width=FW, height=2.5,
                    fill_color=[BG, WARM], fill_opacity=1.0, stroke_width=0)
    bot.set_sheen_direction(DOWN)
    bot.move_to(DOWN * (FH / 2 - 1.25))  # glued to bottom edge

    return VGroup(top, bot)


# ── Persistent HUD ────────────────────────────────────────────────────────────
def build_hud() -> tuple:
    """Top brand bar + bottom watermark. Added once, shown throughout."""
    brand = Text("G I T A  G U R U", font=FONT, font_size=28,
                 color=GOLD, weight=BOLD)
    brand.move_to(UP * HUD_TOP_Y)

    underline = Line(LEFT * 2.0, RIGHT * 2.0,
                     stroke_width=1.2, color=GOLD).set_opacity(0.50)
    underline.next_to(brand, DOWN, buff=0.15)

    hud = VGroup(brand, underline)

    wm = Text("@gita_guru_app  ·  follow for daily wisdom",
              font=FONT, font_size=22, color=MUTED)
    wm.move_to(UP * HUD_BOT_Y)

    return hud, wm


# ── Scene 1  — Sanskrit shloka ───────────────────────────────────────────────
def build_s1(shloka: dict) -> tuple:
    """
    Explicit vertical positions so content fills the portrait frame:
      y= 8.0  verse reference (small, muted)
      y= 4.5  OM  ॐ  (hero element — LARGE)
      y= 1.5  divider
      y=-2.0  Sanskrit body (4 lines, centre)
    """
    ref = Text(
        f"Bhagavad Gita  ·  Chapter {shloka['chapter']},  Verse {shloka['verse']}",
        font=FONT, font_size=24, color=MUTED,
    )
    ref.move_to(UP * 8.0)

    om = Text("ॐ", font=FONT_DEV, font_size=250, color=GOLD_LT)
    om.move_to(UP * 4.0)

    div = make_divider(10.0, DIVCLR, opacity=0.65)
    div.move_to(UP * 1.0)

    sans_lines = [l.strip() for l in shloka["sanskrit"].split("\n") if l.strip()]
    body_mobs  = [Text(l, font=FONT_DEV, font_size=50, color=GOLD)
                  for l in sans_lines]
    body = VGroup(*body_mobs).arrange(DOWN, buff=0.55)
    body.move_to(DOWN * 2.5)

    return ref, om, div, body


# ── Scene 2 & 3  — Translation / Meaning ─────────────────────────────────────
def build_s23(title: str, text: str) -> tuple:
    """
    Explicit vertical positions:
      y= 6.0  section header  (TITLE with dividers)
      y= 0.0  body text        (adaptive font size)
      y=-5.0  ornament ◆ ◆ ◆
    Font size adapts to line count so both 3-line and 4-line texts look balanced.
    """
    # Section header
    div_t = make_divider(10.0)
    lbl   = Text(title.upper(), font=FONT, font_size=60,
                 color=SAFFRON, weight=BOLD)
    div_b = make_divider(10.0)
    hdr   = VGroup(div_t, lbl, div_b).arrange(DOWN, buff=0.30)
    hdr.move_to(UP * 6.0)

    # Body — adaptive sizing
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    n = len(lines)
    fsize = 48 if n <= 3 else 42    # ≤3 lines → 48pt, 4 lines → 42pt
    lbuff = 0.75 if n <= 3 else 0.62

    body_mobs = [Text(l, font=FONT, font_size=fsize, color=WHITE).set_x(0)
                 for l in lines]
    body = VGroup(*body_mobs).arrange(DOWN, buff=lbuff)
    body.move_to(UP * 0.5)

    ornament = Text("◆   ◆   ◆", font=FONT, font_size=18,
                    color=DIVCLR).set_opacity(0.70)
    ornament.move_to(DOWN * 5.0)

    return hdr, body, ornament


# ── Scene 4  — CTA ───────────────────────────────────────────────────────────
def build_s4() -> tuple:
    """
    Stacked from y=4.0 (icon top) downward, filling the middle of the frame.
    Simplified to icon / name / tagline / social-proof / button only.
    """
    if os.path.exists(APP_ICON_PATH):
        icon = ImageMobject(APP_ICON_PATH).set_height(3.5)
    else:
        om_f = Text("ॐ", font=FONT_DEV, font_size=130, color=GOLD)
        ring = Circle(radius=1.6, color=GOLD, stroke_width=1.5)
        icon = VGroup(ring, om_f)

    app_name = Text("GITA GURU", font=FONT, font_size=56,
                    color=GOLD, weight=BOLD)
    tagline  = Text("Your Daily Wisdom from the Bhagavad Gita",
                    font=FONT, font_size=28, color=MUTED)
    div_acc  = make_divider(9.0, DIVCLR, opacity=0.55)
    proof    = Text("Join 10,000+ daily readers",
                    font=FONT, font_size=32, color=WHITE)

    btn_bg  = RoundedRectangle(corner_radius=0.60, width=12.5, height=2.0,
                               fill_color=SAFFRON, fill_opacity=1.0, stroke_width=0)
    btn_lbl = Text("Download Free — Google Play",
                   font=FONT, font_size=36, color=WHITE, weight=BOLD)
    btn_lbl.move_to(btn_bg.get_center())
    btn = VGroup(btn_bg, btn_lbl)

    # Stack from top down — icon centred at y=4.0 so content fills mid-frame
    elems = [icon, app_name, tagline, div_acc, proof, btn]
    gaps  = [0.55, 0.18, 0.65, 0.50, 0.80]

    icon.move_to(UP * 4.0)
    for i in range(1, len(elems)):
        elems[i].next_to(elems[i - 1], DOWN, buff=gaps[i - 1])

    return elems, btn_bg, btn_lbl


# ── Manim Scene ───────────────────────────────────────────────────────────────
class GitaReel(Scene):

    def _stagger_in(self, group, lag: float = 0.18, rt: float = 1.00):
        """Staggered fade-in with gentle upward drift."""
        self.play(
            LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in group],
                        lag_ratio=lag),
            run_time=rt,
        )

    def construct(self):
        shloka, _ = load_shloka()
        self.camera.background_color = BG

        # ── Background depth (always on screen) ───────────────────────────────
        glow = make_ambient_glow()
        self.add(glow)

        # ── Persistent HUD ────────────────────────────────────────────────────
        hud_top, hud_bot = build_hud()
        self.add(hud_top, hud_bot)

        # ── SCENE 1 — Sanskrit ────────────────────────────────────────────────
        s1_ref, s1_om, s1_div, s1_body = build_s1(shloka)

        self.play(FadeIn(s1_ref, shift=DOWN * 0.12), run_time=0.35)
        self.play(FadeIn(s1_om, scale=0.78), run_time=0.70)
        self.play(Create(s1_div), run_time=0.40)
        self._stagger_in(s1_body, lag=0.22, rt=1.55)
        self.wait(1.30)
        self.play(FadeOut(VGroup(s1_ref, s1_om, s1_div, s1_body)), run_time=0.45)
        # S1 ≈ 0.35+0.70+0.40+1.55+1.30+0.45 = 4.75 s

        # ── SCENE 2 — Translation ─────────────────────────────────────────────
        s2_hdr, s2_body, s2_orn = build_s23("Translation", shloka["translation"])

        self.play(FadeIn(s2_hdr), run_time=0.40)
        self._stagger_in(s2_body)
        self.play(FadeIn(s2_orn, scale=0.90), run_time=0.28)
        self.wait(1.80)
        self.play(FadeOut(VGroup(s2_hdr, s2_body, s2_orn)), run_time=0.42)
        # S2 ≈ 0.40+1.00+0.28+1.80+0.42 = 3.90 s

        # ── SCENE 3 — Meaning ─────────────────────────────────────────────────
        s3_hdr, s3_body, s3_orn = build_s23("Meaning", shloka["explanation"])

        self.play(FadeIn(s3_hdr), run_time=0.40)
        self._stagger_in(s3_body)
        self.play(FadeIn(s3_orn, scale=0.90), run_time=0.28)
        self.wait(1.80)
        self.play(FadeOut(VGroup(s3_hdr, s3_body, s3_orn)), run_time=0.42)
        # S3 ≈ 3.90 s

        # ── SCENE 4 — CTA ─────────────────────────────────────────────────────
        s4_elems, btn_bg, btn_lbl = build_s4()
        icon, app_name, tagline, div_acc, proof, btn = s4_elems

        self.play(FadeIn(icon, scale=0.88), run_time=0.55)
        self.play(FadeIn(app_name), FadeIn(tagline), run_time=0.42)
        self.play(Create(div_acc), run_time=0.32)
        self.play(FadeIn(proof), run_time=0.32)
        self.play(GrowFromCenter(btn), run_time=0.60)
        self.play(
            btn_bg.animate.scale(1.04),
            btn_lbl.animate.scale(1.04),
            rate_func=there_and_back, run_time=0.65,
        )
        self.wait(0.85)
        # S4 ≈ 0.50+0.42+0.32+0.30+0.55+0.28+0.65+0.85 = 3.87 s

        # Grand total ≈ 4.75 + 3.90 + 3.90 + 3.87 = 16.42 s


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    shloka, idx = load_shloka()
    script = os.path.basename(__file__)
    os.system(
        f"manim -qh --resolution 1080,1920 --fps 30 "
        f"{script} GitaReel -o {OUTPUT_NAME}.mp4"
    )
    src = os.path.join(RENDER_DIR, f"{OUTPUT_NAME}.mp4")
    if os.path.exists(src):
        os.replace(src, f"{OUTPUT_NAME}.mp4")
        update_progress(idx)
        print(f"Done — shloka {idx} rendered and saved.")
    else:
        print(f"Render output not found at {src!r}")
