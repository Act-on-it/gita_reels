#!/usr/bin/env python3
"""
generate_video_v14.py — Gita Guru · Daily Shloka Reel v14 (Viral Template Redesign)
Instagram-optimised portrait (1080x1920 @ 30fps) Manim video.

STRUCTURE (5 scenes, ~25s total):
  Scene 0 — HOOK      (0–3s)   Pain-point text. Grabs non-followers instantly.
  Scene 1 — SANSKRIT  (3–9s)   OM + verse reference + Sanskrit text
  Scene 2 — ENGLISH   (9–15s)  Translation with highlighted key phrase
  Scene 3 — MEANING   (15–21s) Practical takeaway (what it means for YOUR life)
  Scene 4 — CTA       (21–25s) App icon + "Send this to someone who needs it 🙏"

WHY THIS STRUCTURE:
  - Hook scene fixes the #1 algorithm problem: viewers scroll in first 1.7s
  - "Send this to someone who needs it" at the end is the strongest DM-share trigger
  - Total ~25s: long enough for watch-time signal, short enough to rewatch
  - Each scene has a micro-pause (self.wait) to allow reading before transition

FRAME CONSTANTS (confirmed manim -qh --resolution 1080,1920):
  frame_width  = 14.222 units   x in [-7.11,  7.11]
  frame_height = 25.284 units   y in [-12.64, 12.64]
  pixels_per_unit = 75.9

Instagram Reels safe zone (avoids UI overlays):
  top safe    y < 9.3   (~250px from top)
  bottom safe y > -8.5  (~350px from bottom)
"""

import json, os, sys
from manim import *

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_NAME = "shloka_video"
_STEM = os.path.splitext(os.path.basename(__file__))[0]
RENDER_DIR = f"media/videos/{_STEM}/1920p30"
APP_ICON_PATH = "app_icon.png"

FW = 14.222
FH = 25.284
PPU = 75.9

HUD_TOP_Y = 9.50
HUD_BOT_Y = -8.80

# ── Palette ───────────────────────────────────────────────────────────────────
BG = "#08060D"  # near-black, warm undertone
WARM = "#1A0800"  # deep warm brown (ambient glow edges)
GOLD = "#C9A03F"  # rich gold (Sanskrit text, dividers)
GOLD_LT = "#EDD07A"  # bright gold (OM symbol)
WHITE = "#F2EFE8"  # warm off-white (English body)
SAFFRON = "#E05C0A"  # deep saffron (headers, hook text)
MUTED = "#7A8298"  # slate grey (ref text, watermark)
DIVCLR = "#B09040"  # mid gold (dividers, ornaments)
CREAM = "#FFF5E0"  # warm cream (hook highlight word)
GREEN = "#6FCF97"  # soft green (key phrase highlight in translation)

FONT = "Noto Sans"
FONT_DEV = "Noto Sans Devanagari"

# ── Hooks table ───────────────────────────────────────────────────────────────
# Maps chapter to a relatable life-situation hook.
# Add more as needed. Falls back to DEFAULT if chapter not found.
HOOK_MAP = {
    1: (
        "Feeling confused and\noverwhelmed?",
        "Krishna answered this\n5,000 years ago.",
    ),
    2: ("Feeling stuck and\nnot knowing why?", "The Gita has your answer."),
    3: (
        "Doing everything right\nbut getting no results?",
        "This verse will shift your perspective.",
    ),
    4: ("Doubting yourself\nand your path?", "Read this slowly."),
    5: ("Struggling to stay\ncalm under pressure?", "Ancient wisdom for modern life."),
    6: (
        "Anxious mind that\nwon't stop racing?",
        "Krishna taught the cure 5,000 years ago.",
    ),
    7: ("Searching for meaning\nin what you do?", "This verse changes everything."),
    8: ("Afraid of what\ncomes next in life?", "The Gita speaks to this directly."),
    9: ("Feeling unseen and\nunappreciated?", "This is for you."),
    10: ("Want to do great things\nbut feel small?", "Read this before you give up."),
    11: ("Overwhelmed by life's\nbig picture?", "There is a bigger force at work."),
    12: ("Hard to love people\nwho hurt you?", "The Gita's answer is profound."),
    13: (
        "Not sure who you\nreally are underneath it all?",
        "This verse will ground you.",
    ),
    14: ("Why do you keep\nrepeating the same patterns?", "The Gita explains it."),
    15: (
        "Distracted by every\nshiny thing around you?",
        "This one verse cuts through the noise.",
    ),
    16: ("Surrounded by toxic\nenergy and people?", "Krishna warned us about this."),
    17: ("Not sure if your\nfaith is strong enough?", "This verse will reassure you."),
    18: ("Struggling to let go\nand just do the work?", "BG 18 holds the answer."),
    "DEFAULT": (
        "Feeling lost in\nthe noise of life?",
        "The Gita has always had the answer.",
    ),
}


def get_hook(chapter: int) -> tuple:
    return HOOK_MAP.get(chapter, HOOK_MAP["DEFAULT"])


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


# ── Shared helpers ────────────────────────────────────────────────────────────
def make_divider(width=10.0, color=DIVCLR, opacity=0.80, stroke_w=1.5) -> VGroup:
    hw = width / 2 - 0.22
    left = Line(LEFT * hw, ORIGIN, stroke_width=stroke_w, color=color)
    right = Line(ORIGIN, RIGHT * hw, stroke_width=stroke_w, color=color)
    dot = Dot(radius=0.07, color=color)
    return VGroup(left, dot, right).set_opacity(opacity)


def make_ambient_glow() -> VGroup:
    top = Rectangle(
        width=FW, height=2.5, fill_color=[WARM, BG], fill_opacity=1.0, stroke_width=0
    )
    top.set_sheen_direction(DOWN)
    top.move_to(UP * (FH / 2 - 1.25))
    bot = Rectangle(
        width=FW, height=2.5, fill_color=[BG, WARM], fill_opacity=1.0, stroke_width=0
    )
    bot.set_sheen_direction(DOWN)
    bot.move_to(DOWN * (FH / 2 - 1.25))
    return VGroup(top, bot)


def build_hud() -> tuple:
    brand = Text("G I T A  G U R U", font=FONT, font_size=28, color=GOLD, weight=BOLD)
    brand.move_to(UP * HUD_TOP_Y)
    underline = Line(LEFT * 2.0, RIGHT * 2.0, stroke_width=1.2, color=GOLD).set_opacity(
        0.50
    )
    underline.next_to(brand, DOWN, buff=0.15)
    hud = VGroup(brand, underline)
    wm = Text(
        "@gita_guru_app  ·  follow for daily wisdom",
        font=FONT,
        font_size=20,
        color=MUTED,
    )
    wm.move_to(UP * HUD_BOT_Y)
    return hud, wm


# ── Scene 0 — HOOK ────────────────────────────────────────────────────────────
def build_s0(chapter: int) -> VGroup:
    """
    Full-screen hook. Two stacked text lines in large saffron.
    Line 1: relatable pain-point
    Line 2: curiosity bridge (smaller, muted)

    Layout:
      y= 1.5   Line 1 (large, SAFFRON, bold)
      y=-1.2   Line 2 (medium, MUTED)
    """
    hook_line1, hook_line2 = get_hook(chapter)

    t1_lines = [l for l in hook_line1.split("\n") if l.strip()]
    t2_lines = [l for l in hook_line2.split("\n") if l.strip()]

    g1 = VGroup(
        *[
            Text(l, font=FONT, font_size=80, color=SAFFRON, weight=BOLD)
            for l in t1_lines
        ]
    ).arrange(DOWN, buff=0.40)
    g1.move_to(UP * 1.8)

    g2 = VGroup(
        *[Text(l, font=FONT, font_size=46, color=MUTED) for l in t2_lines]
    ).arrange(DOWN, buff=0.30)
    g2.next_to(g1, DOWN, buff=0.90)

    div = make_divider(8.0, DIVCLR, opacity=0.45)
    div.next_to(g2, DOWN, buff=0.70)

    return VGroup(g1, g2, div)


# ── Scene 1 — Sanskrit ────────────────────────────────────────────────────────
def build_s1(shloka: dict) -> tuple:
    """
    y= 8.0   verse ref (muted, small)
    y= 4.0   OM symbol (hero)
    y= 1.0   divider
    y=-2.5   Sanskrit body
    """
    ref = Text(
        f"Bhagavad Gita · Chapter {shloka['chapter']}, Verse {shloka['verse']}",
        font=FONT,
        font_size=24,
        color=MUTED,
    )
    ref.move_to(UP * 8.0)

    om = Text("ॐ", font=FONT_DEV, font_size=250, color=GOLD_LT)
    om.move_to(UP * 4.0)

    div = make_divider(10.0, DIVCLR, opacity=0.65)
    div.move_to(UP * 1.0)

    sans_lines = [l.strip() for l in shloka["sanskrit"].split("\n") if l.strip()]
    body = VGroup(
        *[Text(l, font=FONT_DEV, font_size=50, color=GOLD) for l in sans_lines]
    ).arrange(DOWN, buff=0.55)
    body.move_to(DOWN * 2.5)

    return ref, om, div, body


# ── Scene 2 — Translation (with key-phrase highlight) ─────────────────────────
def build_s2(shloka: dict) -> tuple:
    """
    y= 6.0   header (TRANSLATION)
    y= 0.5   body lines — first line highlighted in GREEN to draw the eye
    y=-5.0   ornament
    """
    div_t = make_divider(10.0)
    lbl = Text("TRANSLATION", font=FONT, font_size=60, color=SAFFRON, weight=BOLD)
    div_b = make_divider(10.0)
    hdr = VGroup(div_t, lbl, div_b).arrange(DOWN, buff=0.30)
    hdr.move_to(UP * 6.0)

    lines = [l.strip() for l in shloka["translation"].split("\n") if l.strip()]
    n = len(lines)
    fsize = 48 if n <= 3 else 42
    lbuff = 0.75 if n <= 3 else 0.62

    mobs = []
    for i, l in enumerate(lines):
        color = GREEN if i == 0 else WHITE  # highlight first line
        mobs.append(Text(l, font=FONT, font_size=fsize, color=color).set_x(0))
    body = VGroup(*mobs).arrange(DOWN, buff=lbuff)
    body.move_to(UP * 0.5)

    ornament = Text("◆  ◆  ◆", font=FONT, font_size=18, color=DIVCLR).set_opacity(0.70)
    ornament.move_to(DOWN * 5.0)

    return hdr, body, ornament


# ── Scene 3 — Meaning (practical takeaway) ────────────────────────────────────
def build_s3(shloka: dict) -> tuple:
    """
    y= 6.0   header (MEANING / WHAT IT MEANS FOR YOU)
    y= 0.5   body lines
    y=-5.0   ornament

    The header is intentionally changed to "WHAT IT MEANS FOR YOU" to make
    the scene feel personally relevant, not textbook-academic.
    """
    div_t = make_divider(10.0)
    lbl = Text(
        "WHAT IT MEANS FOR YOU", font=FONT, font_size=48, color=SAFFRON, weight=BOLD
    )
    div_b = make_divider(10.0)
    hdr = VGroup(div_t, lbl, div_b).arrange(DOWN, buff=0.30)
    hdr.move_to(UP * 6.0)

    lines = [l.strip() for l in shloka["explanation"].split("\n") if l.strip()]
    n = len(lines)
    fsize = 48 if n <= 3 else 42
    lbuff = 0.75 if n <= 3 else 0.62

    body = VGroup(
        *[Text(l, font=FONT, font_size=fsize, color=WHITE).set_x(0) for l in lines]
    ).arrange(DOWN, buff=lbuff)
    body.move_to(UP * 0.5)

    ornament = Text("◆  ◆  ◆", font=FONT, font_size=18, color=DIVCLR).set_opacity(0.70)
    ornament.move_to(DOWN * 5.0)

    return hdr, body, ornament


# ── Scene 4 — CTA (DM-share trigger) ─────────────────────────────────────────
def build_s4() -> tuple:
    """
    The most important change from v13:
    Primary CTA is now "Send this to someone who needs it 🙏"
    This is the strongest DM-share trigger on Instagram.
    The app download button is secondary (below).

    Layout:
      y= 5.0   app icon
      y= 2.5   GITA GURU name
      y= 1.6   tagline
      y= 0.5   divider
      y=-0.5   share CTA (large, CREAM, bold) ← NEW PRIMARY CTA
      y=-2.8   download button (secondary)
      y=-4.5   @handle reminder
    """
    # App icon / OM fallback
    if os.path.exists(APP_ICON_PATH):
        icon = ImageMobject(APP_ICON_PATH).set_height(3.0)
    else:
        om_f = Text("ॐ", font=FONT_DEV, font_size=130, color=GOLD)
        ring = Circle(radius=1.6, color=GOLD, stroke_width=1.5)
        icon = VGroup(ring, om_f)
    icon.move_to(UP * 5.0)

    app_name = Text("GITA GURU", font=FONT, font_size=56, color=GOLD, weight=BOLD)
    app_name.next_to(icon, DOWN, buff=0.35)

    tagline = Text(
        "Your Daily Wisdom from the Bhagavad Gita", font=FONT, font_size=26, color=MUTED
    )
    tagline.next_to(app_name, DOWN, buff=0.20)

    div_acc = make_divider(9.0, DIVCLR, opacity=0.55)
    div_acc.next_to(tagline, DOWN, buff=0.55)

    # ── PRIMARY CTA: share trigger ──
    share_line1 = Text(
        "Send this to someone", font=FONT, font_size=54, color=CREAM, weight=BOLD
    )
    share_line2 = Text(
        "who needs it today 🙏", font=FONT, font_size=54, color=CREAM, weight=BOLD
    )
    share_cta = VGroup(share_line1, share_line2).arrange(DOWN, buff=0.28)
    share_cta.next_to(div_acc, DOWN, buff=0.60)

    # ── SECONDARY CTA: download ──
    btn_bg = RoundedRectangle(
        corner_radius=0.55,
        width=12.5,
        height=1.80,
        fill_color=SAFFRON,
        fill_opacity=1.0,
        stroke_width=0,
    )
    btn_lbl = Text(
        "Download Free — Google Play", font=FONT, font_size=32, color=WHITE, weight=BOLD
    )
    btn_lbl.move_to(btn_bg.get_center())
    btn = VGroup(btn_bg, btn_lbl)
    btn.next_to(share_cta, DOWN, buff=0.75)

    handle = Text("@gita_guru_app", font=FONT, font_size=26, color=MUTED)
    handle.next_to(btn, DOWN, buff=0.45)

    return icon, app_name, tagline, div_acc, share_cta, btn, btn_bg, btn_lbl, handle


# ── Main Scene ─────────────────────────────────────────────────────────────────
class GitaReel(Scene):

    def _stagger_in(self, group, lag=0.18, rt=1.00):
        self.play(
            LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in group], lag_ratio=lag),
            run_time=rt,
        )

    def construct(self):
        shloka, _ = load_shloka()
        self.camera.background_color = BG

        # Always-on background depth and HUD
        self.add(make_ambient_glow())
        hud_top, hud_bot = build_hud()
        self.add(hud_top, hud_bot)

        # ── SCENE 0 — HOOK (0–3s) ─────────────────────────────────────────
        s0 = build_s0(shloka["chapter"])
        self.play(FadeIn(s0[0], shift=UP * 0.20), run_time=0.50)  # pain-point
        self.play(FadeIn(s0[1], shift=UP * 0.12), run_time=0.35)  # bridge text
        self.play(Create(s0[2]), run_time=0.25)  # divider
        self.wait(1.60)  # reading pause
        self.play(FadeOut(s0), run_time=0.35)
        # S0 ≈ 0.50+0.35+0.25+1.60+0.35 = 3.05s

        # ── SCENE 1 — SANSKRIT (3–9s) ─────────────────────────────────────
        s1_ref, s1_om, s1_div, s1_body = build_s1(shloka)
        self.play(FadeIn(s1_ref, shift=DOWN * 0.12), run_time=0.32)
        self.play(FadeIn(s1_om, scale=0.78), run_time=0.70)
        self.play(Create(s1_div), run_time=0.38)
        self._stagger_in(s1_body, lag=0.22, rt=1.55)
        self.wait(1.50)
        self.play(FadeOut(VGroup(s1_ref, s1_om, s1_div, s1_body)), run_time=0.42)
        # S1 ≈ 0.32+0.70+0.38+1.55+1.50+0.42 = 4.87s

        # ── SCENE 2 — TRANSLATION (9–15s) ─────────────────────────────────
        s2_hdr, s2_body, s2_orn = build_s2(shloka)
        self.play(FadeIn(s2_hdr), run_time=0.38)
        self._stagger_in(s2_body, lag=0.20, rt=1.00)
        self.play(FadeIn(s2_orn, scale=0.90), run_time=0.25)
        self.wait(2.00)  # longer pause — let them read + connect
        self.play(FadeOut(VGroup(s2_hdr, s2_body, s2_orn)), run_time=0.40)
        # S2 ≈ 0.38+1.00+0.25+2.00+0.40 = 4.03s

        # ── SCENE 3 — MEANING (15–21s) ────────────────────────────────────
        s3_hdr, s3_body, s3_orn = build_s3(shloka)
        self.play(FadeIn(s3_hdr), run_time=0.38)
        self._stagger_in(s3_body, lag=0.20, rt=1.00)
        self.play(FadeIn(s3_orn, scale=0.90), run_time=0.25)
        self.wait(2.00)
        self.play(FadeOut(VGroup(s3_hdr, s3_body, s3_orn)), run_time=0.40)
        # S3 ≈ 4.03s

        # ── SCENE 4 — CTA (21–25s) ────────────────────────────────────────
        icon, app_name, tagline, div_acc, share_cta, btn, btn_bg, btn_lbl, handle = (
            build_s4()
        )

        self.play(FadeIn(icon, scale=0.88), run_time=0.45)
        self.play(FadeIn(app_name), FadeIn(tagline), run_time=0.38)
        self.play(Create(div_acc), run_time=0.28)

        # Share CTA pulses in — this is the money moment
        self.play(GrowFromCenter(share_cta), run_time=0.55)
        self.play(
            share_cta.animate.scale(1.05),
            rate_func=there_and_back,
            run_time=0.50,
        )
        self.wait(0.40)

        self.play(GrowFromCenter(btn), run_time=0.45)
        self.play(FadeIn(handle), run_time=0.30)

        # Subtle pulse on download button to invite tap
        self.play(
            btn_bg.animate.scale(1.03),
            btn_lbl.animate.scale(1.03),
            rate_func=there_and_back,
            run_time=0.55,
        )
        self.wait(0.80)
        # S4 ≈ 0.45+0.38+0.28+0.55+0.50+0.40+0.45+0.30+0.55+0.80 = 4.66s

        # Grand total ≈ 3.05 + 4.87 + 4.03 + 4.03 + 4.66 = ~20.64s
        # Add any inter-scene .wait() above to tune to 23–26s target


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
        print(f"Done — shloka {idx} rendered to {OUTPUT_NAME}.mp4")
    else:
        print(f"Render output not found at {src!r}")
