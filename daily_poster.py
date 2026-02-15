import os
import requests
import urllib.parse
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
VIDEO_DIR = 'videos/'
HISTORY_FILE = 'sent_history.txt'
GITHUB_USER = "Automation8248"
GITHUB_REPO = "M-Tone"
BRANCH = "main"

# ⏳ Retention Policy (Kitne din baad delete karna hai)
DELETE_AFTER_DAYS = 15

# SEO Hashtags
SEO_HASHTAGS = "#LofiHindi #SadLofi #SlowedReverb #MidnightVibes #HindiSongs #ArijitSingh #BrokenHeart #MusicLover #IndianLofi"

# Fallback Content
DEFAULT_TITLE = "Midnight Memories"
DEFAULT_CAPTION = "Lost in the echo of silence."

def generate_clean_lofi_content():
    """
    Generates clean content (No Stars, No Hashtags in Title).
    """
    prompt = (
        "Write a deep, poetic, and emotional title and a 1-sentence short caption for a Hindi Lofi Music video. "
        "Theme: Sadness, Night, Rain, Lost Love, Silence. "
        "Style: Aesthetic, Heart touching. "
        "Language: Hinglish (Hindi + English mix). "
        "Format: TITLE | CAPTION "
        "IMPORTANT RULES: "
        "1. Do NOT use hashtags (#). "
        "2. Do NOT use stars (*) or bold formatting. "
        "3. Do NOT use the word 'AI' or 'Generated'. "
        "4. Keep the caption very short."
    )
    
    seed = random.randint(1, 999999)
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}?seed={seed}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            text = response.text.strip()
            clean_text = text.replace('*', '').replace('#', '').replace('"', '').replace('New video post', '')
            
            if "|" in clean_text:
                parts = clean_text.split("|")
                return parts[0].strip(), parts[1].strip()
            else:
                return clean_text, "Late night vibes."
    except Exception as e:
        print(f"AI Generation Failed: {e}")
    
    return DEFAULT_TITLE, DEFAULT_CAPTION

def manage_retention_policy():
    """
    🛑 CRITICAL FUNCTION:
    Ye function har bar run hone par check karega ki koi video 15 din se purani to nahi hai?
    Agar hai, to usko Folder se aur History se delete kar dega.
    """
    if not os.path.exists(HISTORY_FILE):
        return

    print("🔍 Checking for expired videos (Older than 15 days)...")
    
    with open(HISTORY_FILE, 'r') as f:
        lines = f.read().splitlines()
    
    updated_history = []
    today = datetime.now()
    deleted_count = 0
    
    for line in lines:
        try:
            # Expected Format: video_name.mp4 | 2026-02-15
            if "|" in line:
                parts = line.split("|")
                video_name = parts[0].strip()
                date_str = parts[1].strip()
                
                # Calculate Age
                post_date = datetime.strptime(date_str, "%Y-%m-%d")
                age = (today - post_date).days
                
                if age >= DELETE_AFTER_DAYS:
                    # 🗑️ DELETE LOGIC
                    file_path = os.path.join(VIDEO_DIR, video_name)
                    
                    # Delete actual file if exists
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"❌ DELETED EXPIRED FILE: {video_name} ({age} days old)")
                    else:
                        print(f"⚠️ File already gone: {video_name}")
                    
                    deleted_count += 1
                    # Isko updated_history mein add NAHI karenge (yani delete ho gaya list se)
                else:
                    # Keep valid entry
                    updated_history.append(line)
            else:
                # Agar format match na ho (purana data), to usko safe rakho
                updated_history.append(line)

        except Exception as e:
            print(f"Error checking line '{line}': {e}")
            updated_history.append(line)
    
    # 💾 Save Cleaned History
    if deleted_count > 0:
        with open(HISTORY_FILE, 'w') as f:
            for entry in updated_history:
                f.write(f"{entry}\n")
        print(f"✅ Cleanup Done. Removed {deleted_count} old videos from history.")
    else:
        print("✅ No expired videos found.")

def get_next_video():
    if not os.path.exists(VIDEO_DIR):
        print(f"Error: '{VIDEO_DIR}' folder nahi mila.")
        return None
    
    # Get all video files
    all_videos = sorted([f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.mov'))])
    
    # Read history to see what is already posted
    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, 'w').close()
    
    with open(HISTORY_FILE, 'r') as f:
        history_data = f.read()

    # Find first video that is NOT in history
    for video in all_videos:
        if video not in history_data:
            return video
    return None

def send_daily_post(video_name):
    video_path = os.path.join(VIDEO_DIR, video_name)
    
    # 1. Generate Content
    print("Generating Content...")
    title, caption = generate_clean_lofi_content()
    
    # 2. Telegram Caption
    tg_caption = (
        f"{title}\n\n"
        f"{caption}\n"
        f".\n"
        f".\n"
        f".\n"
        f"{SEO_HASHTAGS}"
    )
    
    # 3. Webhook Link
    video_link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/{VIDEO_DIR}{video_name}"
    video_link = video_link.replace(" ", "%20")

    print(f"Sending Title: {title}")

    # 4. Telegram Send
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    sent_success = False
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        with open(video_path, 'rb') as video:
            try:
                response = requests.post(url, data={'chat_id': chat_id, 'caption': tg_caption}, files={'video': video})
                if response.status_code == 200:
                    print("Telegram: Sent successfully.")
                    sent_success = True
                else:
                    print(f"Telegram Failed: {response.text}")
            except Exception as e:
                print(f"Telegram Error: {e}")

    # 5. Webhook Send
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        try:
            payload = {
                "content": f"🚀 **Posted**\nTitle: {title}\nLink: {video_link}",
                "embeds": [{
                    "title": title,
                    "description": caption,
                    "url": video_link,
                    "color": 5814783,
                    "fields": [{"name": "Status", "value": "Posted to Telegram", "inline": True}]
                }]
            }
            requests.post(webhook_url, json=payload)
        except Exception as e:
            print(f"Webhook Error: {e}")
            
    return sent_success

# --- MAIN EXECUTION FLOW ---

# 1️⃣ Step 1: Retention Policy Check (Delete 15+ days old videos)
manage_retention_policy()

# 2️⃣ Step 2: Select New Video
video_to_send = get_next_video()

if video_to_send:
    print(f"🎥 Processing New Video: {video_to_send}")
    
    # 3️⃣ Step 3: Send Video
    success = send_daily_post(video_to_send)
    
    if success:
        # 4️⃣ Step 4: Update History with Date (Important for retention logic)
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_entry = f"{video_to_send} | {today_str}"
        
        with open(HISTORY_FILE, 'a') as f:
            f.write(log_entry + '\n')
            
        print(f"✅ History Updated: {log_entry}")
    else:
        print("❌ Sending failed. History NOT updated.")

else:
    print("⚠️ No new videos found to post.")
