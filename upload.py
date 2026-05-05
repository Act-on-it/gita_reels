import json
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
        f"🙏 Bhagavad Gita · Chapter {shloka['chapter']}, Verse {shloka['verse']}\n\n"
        f"📖 {shloka['translation']}\n\n"
        f"💡 {shloka['explanation']}\n\n"
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
