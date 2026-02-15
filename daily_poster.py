import os
import requests
import urllib.parse

# --- CONFIGURATION ---
VIDEO_DIR = 'videos/'
GITHUB_USER = "Automation8248"
GITHUB_REPO = "M-Tone"
BRANCH = "main"

# SEO Hashtags (Fixed)
SEO_HASHTAGS = "#LofiHindi #SadLofi #SlowedReverb #MidnightVibes #HindiSongs #ArijitSingh #BrokenHeart #MusicLover #IndianLofi"

# Fallback Content
DEFAULT_TITLE = "Khamosh Raatein"
DEFAULT_CAPTION = "Headphones lagayein aur kho jayein."

def generate_clean_lofi_content():
    """
    Pollinations AI se content likhwata hai.
    Strictly NO Hashtags, NO Stars via Prompt Engineering + Cleaning.
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
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.text.strip()
            # Double Cleaning to be safe
            clean_text = text.replace('*', '').replace('#', '').replace('"', '')
            
            if "|" in clean_text:
                parts = clean_text.split("|")
                return parts[0].strip(), parts[1].strip()
            else:
                return clean_text, "Late night vibes."
    except Exception as e:
        print(f"AI Generation Failed: {e}")
    
    return DEFAULT_TITLE, DEFAULT_CAPTION

def get_next_video():
    if not os.path.exists(VIDEO_DIR):
        print(f"Error: '{VIDEO_DIR}' folder nahi mila.")
        return None
    
    # Folder ki sabse pehli video uthayega
    all_videos = sorted([f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.mov'))])
    
    if all_videos:
        return all_videos[0]  # First video
    return None

def send_daily_post(video_name):
    video_path = os.path.join(VIDEO_DIR, video_name)
    
    # 1. Generate Content
    print("Generating Content...")
    title, caption = generate_clean_lofi_content()
    
    # 2. Telegram Caption Format (Aapka manga hua format)
    tg_caption = (
        f"New video post\n\n"
        f"🎵 **{title}**\n\n"
        f"{caption}\n"
        f".\n"
        f".\n"
        f".\n"
        f"{SEO_HASHTAGS}"
    )
    
    # 3. Generate Video Link (Webhook ke liye)
    video_link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/{VIDEO_DIR}{video_name}"
    video_link = video_link.replace(" ", "%20")

    print(f"Sending: {title}")

    # 4. Send to Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    sent_success = False
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        with open(video_path, 'rb') as video:
            try:
                # Telegram Post
                response = requests.post(url, data={'chat_id': chat_id, 'caption': tg_caption}, files={'video': video})
                if response.status_code == 200:
                    print("Telegram: Sent successfully.")
                    sent_success = True
                else:
                    print(f"Telegram Failed: {response.text}")
            except Exception as e:
                print(f"Telegram Error: {e}")

    # 5. Send to Webhook (Rich Data Restored)
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        try:
            # Full JSON Payload wapas add kar diya hai
            payload = {
                "content": f"🚀 **New Post Live**\nTitle: {title}\nLink: {video_link}",
                "embeds": [{
                    "title": title,
                    "description": caption,
                    "url": video_link,
                    "color": 5814783,
                    "fields": [
                        {"name": "Status", "value": "Posted to Telegram", "inline": True},
                        {"name": "Hashtags", "value": SEO_HASHTAGS, "inline": False}
                    ]
                }]
            }
            requests.post(webhook_url, json=payload)
            print("Webhook: Sent successfully.")
        except Exception as e:
            print(f"Webhook Error: {e}")
            
    return sent_success

# --- EXECUTION ---
video_to_send = get_next_video()

if video_to_send:
    print(f"Processing: {video_to_send}")
    
    # Send Video
    success = send_daily_post(video_to_send)
    
    # DELETE LOGIC
    if success:
        file_path = os.path.join(VIDEO_DIR, video_to_send)
        try:
            os.remove(file_path)
            print(f"🗑️ DELETED: {video_to_send} removed from folder.")
        except Exception as e:
            print(f"Error deleting file: {e}")
    else:
        print("Sending failed, video NOT deleted.")

else:
    print("No videos found in folder.")
