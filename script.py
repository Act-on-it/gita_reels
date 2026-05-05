# Writing all project files

import json
import os
os.makedirs("output/gita-reels/.github/workflows", exist_ok=True)
os.makedirs("output/gita-reels", exist_ok=True)

# 1. generate_video.py
generate_video = '''import json
import os
import sys
from manim import *

PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.arime.gita_guru"
BG_COLOR       = "#1a1a2e"
GOLD           = "#FFD700"
WHITE          = "#F5F5F5"
SAFFRON        = "#FF6B35"
OUTPUT_FILE    = "shloka_video.mp4"

def load_shloka():
    with open("progress.json") as f:
        progress = json.load(f)
    idx = progress["last_posted_index"] + 1

    with open("shlokas.json", encoding="utf-8") as f:
        shlokas = json.load(f)

    if idx >= len(shlokas):
        print("All shlokas posted!")
        sys.exit(0)

    return shlokas[idx], idx


class GitaReel(Scene):
    def construct(self):
        shloka, _ = load_shloka()
        self.camera.background_color = BG_COLOR

        # ── Scene 1: Sanskrit Shloka (5 sec) ──────────────────────────────
        chapter_label = Text(
            f"Bhagavad Gita · Chapter {shloka['chapter']}, Verse {shloka['verse']}",
            font="Noto Sans",
            font_size=22,
            color=SAFFRON,
        ).to_edge(UP, buff=0.4)

        sanskrit = Text(
            shloka["sanskrit"],
            font="Noto Sans Devanagari",
            font_size=40,
            color=GOLD,
            line_spacing=1.4,
        ).move_to(ORIGIN)

        divider = Line(LEFT * 3, RIGHT * 3, color=GOLD, stroke_width=1).next_to(sanskrit, DOWN, buff=0.3)

        self.play(FadeIn(chapter_label), run_time=0.5)
        self.play(Write(sanskrit), run_time=1.5)
        self.play(Create(divider), run_time=0.5)
        self.wait(2.5)
        self.play(FadeOut(sanskrit), FadeOut(divider), FadeOut(chapter_label), run_time=0.5)

        # ── Scene 2: English Translation (5 sec) ──────────────────────────
        translation_label = Text(
            "Translation",
            font="Noto Sans",
            font_size=24,
            color=SAFFRON,
        ).to_edge(UP, buff=0.4)

        translation = Text(
            shloka["translation"],
            font="Noto Sans",
            font_size=34,
            color=WHITE,
            line_spacing=1.5,
        ).move_to(ORIGIN)

        self.play(FadeIn(translation_label), run_time=0.4)
        self.play(FadeIn(translation, shift=UP * 0.3), run_time=0.8)
        self.wait(3.3)
        self.play(FadeOut(translation), FadeOut(translation_label), run_time=0.5)

        # ── Scene 3: Explanation (5 sec) ──────────────────────────────────
        explanation_label = Text(
            "Meaning",
            font="Noto Sans",
            font_size=24,
            color=SAFFRON,
        ).to_edge(UP, buff=0.4)

        lotus = Text("🪷", font_size=36).next_to(explanation_label, RIGHT, buff=0.2)

        explanation = Text(
            shloka["explanation"],
            font="Noto Sans",
            font_size=30,
            color=WHITE,
            line_spacing=1.6,
        ).move_to(ORIGIN)

        self.play(FadeIn(explanation_label), FadeIn(lotus), run_time=0.4)
        self.play(FadeIn(explanation, shift=UP * 0.3), run_time=0.8)
        self.wait(3.3)
        self.play(FadeOut(explanation), FadeOut(explanation_label), FadeOut(lotus), run_time=0.5)

        # ── Scene 4: CTA (3 sec) ──────────────────────────────────────────
        cta_heading = Text(
            "Explore all 700 Shlokas",
            font="Noto Sans",
            font_size=30,
            color=GOLD,
        ).shift(UP * 1.2)

        cta_box = RoundedRectangle(
            corner_radius=0.2,
            width=5.5,
            height=0.9,
            fill_color=SAFFRON,
            fill_opacity=1,
            stroke_width=0,
        ).shift(DOWN * 0.2)

        cta_text = Text(
            "Download Gita Guru App  →",
            font="Noto Sans",
            font_size=28,
            color=WHITE,
            weight=BOLD,
        ).move_to(cta_box.get_center())

        url_text = Text(
            PLAY_STORE_URL,
            font="Noto Sans",
            font_size=16,
            color=GOLD,
        ).next_to(cta_box, DOWN, buff=0.3)

        self.play(FadeIn(cta_heading), run_time=0.4)
        self.play(FadeIn(cta_box), FadeIn(cta_text), run_time=0.5)
        self.play(FadeIn(url_text), run_time=0.3)
        self.wait(1.8)


def update_progress(idx):
    with open("progress.json", "w") as f:
        json.dump({"last_posted_index": idx}, f)


if __name__ == "__main__":
    shloka, idx = load_shloka()

    # Render at 1080x1920 (portrait) for Reels
    os.system(
        f\'manim -qh --resolution 1080,1920 --fps 30 generate_video.py GitaReel -o {OUTPUT_FILE}\'
    )

    # Move rendered file to root (Manim outputs to media/ by default)
    rendered = f"media/videos/generate_video/1080p30/{OUTPUT_FILE}"
    if os.path.exists(rendered):
        os.rename(rendered, OUTPUT_FILE)
        print(f"Video rendered: {OUTPUT_FILE}")
        update_progress(idx)
    else:
        print("Render failed — check Manim output above.")
        sys.exit(1)
'''

# 2. upload.py
upload_py = '''import json
import os
import requests
import time

POSTIZ_API_KEY      = os.environ["POSTIZ_API_KEY"]
INSTAGRAM_PROFILE   = os.environ["INSTAGRAM_PROFILE_ID"]
VIDEO_FILE          = "shloka_video.mp4"
POSTIZ_BASE_URL     = "https://app.postiz.com/api/v1"

def load_current_shloka():
    with open("progress.json") as f:
        idx = json.load(f)["last_posted_index"]
    with open("shlokas.json", encoding="utf-8") as f:
        shlokas = json.load(f)
    return shlokas[idx]

def build_caption(shloka):
    return (
        f"🙏 Bhagavad Gita · Chapter {shloka[\'chapter\']}, Verse {shloka[\'verse\']}\\n\\n"
        f"📖 {shloka[\'translation\']}\\n\\n"
        f"💡 {shloka[\'explanation\']}\\n\\n"
        f"#BhagavadGita #GitaDaily #SanatanDharma #Krishna #Spirituality "
        f"#GitaGuru #DailyWisdom #HinduPhilosophy #Shloka #Motivation"
    )

def upload_video():
    shloka = load_current_shloka()
    caption = build_caption(shloka)

    headers = {
        "Authorization": f"Bearer {POSTIZ_API_KEY}",
    }

    # Step 1: Upload media file
    with open(VIDEO_FILE, "rb") as f:
        upload_resp = requests.post(
            f"{POSTIZ_BASE_URL}/media/upload",
            headers=headers,
            files={"file": (VIDEO_FILE, f, "video/mp4")},
        )
    upload_resp.raise_for_status()
    media_id = upload_resp.json()["id"]
    print(f"Media uploaded: {media_id}")

    # Step 2: Schedule post (post immediately = now)
    post_payload = {
        "profileId": INSTAGRAM_PROFILE,
        "content": caption,
        "mediaIds": [media_id],
        "type": "reel",
        "publishNow": True,
    }

    post_resp = requests.post(
        f"{POSTIZ_BASE_URL}/posts",
        headers={**headers, "Content-Type": "application/json"},
        json=post_payload,
    )
    post_resp.raise_for_status()
    print(f"Posted successfully: {post_resp.json()}")

if __name__ == "__main__":
    upload_video()
'''

# 3. shlokas.json (sample with 3 shlokas)
shlokas_json = json.dumps([
    {
        "chapter": 2,
        "verse": 47,
        "sanskrit": "कर्मण्येवाधिकारस्ते\nमा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा\nते सङ्गोऽस्त्वकर्मणि॥",
        "translation": "You have a right to perform\nyour prescribed duties,\nbut you are not entitled to\nthe fruits of your actions.",
        "explanation": "Act without attachment to results.\nFocus on effort, not outcome.\nThis is the essence of Nishkama Karma."
    },
    {
        "chapter": 2,
        "verse": 14,
        "sanskrit": "मात्रास्पर्शास्तु कौन्तेय\nशीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्\nतांस्तितिक्षस्व भारत॥",
        "translation": "O son of Kunti, the contacts\nbetween the senses and sense objects\ngive rise to fleeting perceptions\nof happiness and distress.",
        "explanation": "Joy and sorrow are temporary.\nEndure them with patience and equanimity.\nDo not be swayed by passing feelings."
    },
    {
        "chapter": 4,
        "verse": 7,
        "sanskrit": "यदा यदा हि धर्मस्य\nग्लानिर्भवति भारत।\nअभ्युत्थानमधर्मस्य\nतदात्मानं सृजाम्यहम्॥",
        "translation": "Whenever righteousness declines\nand unrighteousness rises,\nO Bharata, at that time\nI manifest Myself.",
        "explanation": "God incarnates whenever\ndharma is in danger.\nDivine intervention restores balance\nand protects the good."
    }
], ensure_ascii=False, indent=2)

# 4. progress.json
progress_json = json.dumps({"last_posted_index": -1}, indent=2)

# 5. GitHub Actions workflow
workflow_yml = """name: Daily Gita Reel

on:
  schedule:
    - cron: '30 1 * * *'   # 7:00 AM IST (1:30 AM UTC)
  workflow_dispatch:         # Allow manual trigger for testing

jobs:
  post-reel:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # Needed to commit progress.json back

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update -y
          sudo apt-get install -y \\
            ffmpeg \\
            fonts-noto \\
            fonts-noto-cjk \\
            fonts-noto-color-emoji \\
            texlive-latex-base \\
            texlive-fonts-recommended \\
            libcairo2-dev \\
            libpango1.0-dev

      - name: Install Python dependencies
        run: |
          pip install manim requests

      - name: Generate video
        run: python generate_video.py

      - name: Upload to Instagram
        env:
          POSTIZ_API_KEY: ${{ secrets.POSTIZ_API_KEY }}
          INSTAGRAM_PROFILE_ID: ${{ secrets.INSTAGRAM_PROFILE_ID }}
        run: python upload.py

      - name: Commit updated progress
        run: |
          git config user.name  "Gita Bot"
          git config user.email "bot@gita-guru.app"
          git add progress.json
          git diff --cached --quiet || git commit -m "chore: posted shloka index $(python -c \\"import json; print(json.load(open('progress.json'))['last_posted_index'])\\")"
          git push
"""

# Write all files
files = {
    "output/gita-reels/generate_video.py": generate_video,
    "output/gita-reels/upload.py": upload_py,
    "output/gita-reels/shlokas.json": shlokas_json,
    "output/gita-reels/progress.json": progress_json,
    "output/gita-reels/.github/workflows/daily_post.yml": workflow_yml,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {path}")

print("\nAll files generated successfully.")