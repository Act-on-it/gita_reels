#!/usr/bin/env python3
"""
upload.py — Post reel directly to Instagram via Meta Graph API (100% free)
No third-party service needed.
"""

import os, json, time, requests

ACCESS_TOKEN     = os.environ["IG_ACCESS_TOKEN"]
IG_USER_ID       = os.environ["IG_USER_ID"]
VIDEO_URL        = os.environ["VIDEO_URL"]   # public URL to the uploaded video
GRAPH_URL        = f"https://graph.instagram.com/v21.0/{IG_USER_ID}"

def get_current_shloka():
    with open("progress.json") as f:
        idx = json.load(f)["last_posted_index"]
    with open("shlokas.json", encoding="utf-8") as f:
        shlokas = json.load(f)
    return shlokas[idx]

def build_caption(s):
    hashtags = (
        "#BhagavadGita #GeetaQuotes #SanatanDharma #HinduWisdom "
        "#DailyGita #GitaGuru #VedicWisdom #Spirituality #Krishna "
        "#GitaShloka #BhagavadGitaQuotes #Hinduism #DailyWisdom "
        "#AncientWisdom #InnerPeace"
    )
    return (
        f"📖 Bhagavad Gita — Chapter {s['chapter']}, Verse {s['verse']}\n\n"
        f"🕉️ {s['sanskrit'].replace(chr(10), ' ')}\n\n" # Sanskrit with line breaks replaced by spaces
        f"{s['translation'].replace(chr(10), ' ')}\n\n" # English translation with line breaks replaced by spaces
        f"💡 {s['explanation'].replace(chr(10), ' ')}\n\n" # English explanation with line breaks replaced by spaces
        f"Download Gita Guru — Free on Play Store 🙏\n\n"
        f"{hashtags}"
    )

def post_reel(caption: str):
    # Step 1 — Create media container
    print("Creating media container...")
    payload = {
        "media_type":   "REELS",
        "video_url":    VIDEO_URL,
        "caption":      caption,
        "access_token": ACCESS_TOKEN,
    }
    resp = requests.post(f"{GRAPH_URL}/media", data=payload)

    # ── Print full error details before raising ──
    if not resp.ok:
        print(f"\n❌ HTTP {resp.status_code} Error")
        try:
            err = resp.json()
            print(f"   Error type    : {err.get('error', {}).get('type', 'unknown')}")
            print(f"   Error code    : {err.get('error', {}).get('code', 'unknown')}")
            print(f"   Error subcode : {err.get('error', {}).get('error_subcode', 'unknown')}")
            print(f"   Message       : {err.get('error', {}).get('message', 'unknown')}")
            print(f"   Full response : {json.dumps(err, indent=2)}")
        except Exception:
            print(f"   Raw response  : {resp.text}")
        resp.raise_for_status()

    container_id = resp.json()["id"]
    print(f"  ✅ Container ID: {container_id}")

    # Step 2 — Wait for Meta to process video
    print("Waiting for Meta to process video...")
    for attempt in range(15):
        time.sleep(20)
        status_resp = requests.get(
            f"https://graph.instagram.com/v21.0/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN}
        )
        status = status_resp.json().get("status_code", "")
        print(f"  Attempt {attempt+1}: status = {status}")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError("Meta returned ERROR while processing video.")
    else:
        raise TimeoutError("Video processing timed out.")

    # Step 3 — Publish
    print("Publishing reel...")
    pub_resp = requests.post(
        f"{GRAPH_URL}/media_publish",
        data={
            "creation_id":  container_id,
            "access_token": ACCESS_TOKEN,
        }
    )
    if not pub_resp.ok:
        print(f"\n❌ Publish error: {pub_resp.text}")
        pub_resp.raise_for_status()

    post_id = pub_resp.json()["id"]
    print(f"✅ Reel published! Post ID: {post_id}")


def verify_credentials():
    """Quick check that token and user ID are valid before attempting to post."""
    print("🔍 Verifying credentials...")
    r = requests.get(
        f"https://graph.instagram.com/v21.0/{IG_USER_ID}",
        params={"fields": "id,name,username,account_type", "access_token": ACCESS_TOKEN}
    )
    if not r.ok:
        print(f"❌ Credential check failed: {r.json()}")
        r.raise_for_status()
    data = r.json()
    print(f"  ✅ Authenticated as: @{data.get('username')} (ID: {data.get('id')})")
    print(f"     Account type    : {data.get('account_type')}")

    # Also check VIDEO_URL is reachable
    print(f"\n🔍 Checking video URL is publicly accessible...")
    head = requests.head(VIDEO_URL, timeout=10, allow_redirects=True)
    print(f"  URL   : {VIDEO_URL}")
    print(f"  Status: {head.status_code}")
    ct = head.headers.get("Content-Type", "unknown")
    print(f"  Type  : {ct}")
    # if head.status_code != 200:
    #     raise RuntimeError(f"Video URL returned {head.status_code} — Meta cannot access it!")
    # if "video" not in ct and "octet" not in ct:
    #     print(f"  ⚠️  WARNING: Content-Type is '{ct}' — should be video/mp4")
    # else:
    #     print(f"  ✅ Video URL is accessible")


if __name__ == "__main__":
    verify_credentials()
    shloka  = get_current_shloka()
    caption = build_caption(shloka)
    print(f"\n📤 Posting BG {shloka['chapter']}.{shloka['verse']}...")
    post_reel(caption)