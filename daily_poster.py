import os
import requests
import urllib.parse

# --- CONFIGURATION (Extracted from your Screenshot) ---
VIDEO_DIR = 'videos/'
HISTORY_FILE = 'sent_history.txt'
GITHUB_USER = "Automation8248"  # Fixed from image
GITHUB_REPO = "M-Tone"          # Fixed from image
BRANCH = "main"                 # Usually 'main' by default

# Fallback Content
DEFAULT_TITLE = "Khamosh Raatein aur Bikhri Yaadein"
DEFAULT_CAPTION = "Headphones lagayein aur kho jayein in yaadon mein."

def generate_clean_lofi_content():
    """
    Pollinations AI se content likhwata hai.
    STRICTLY NO HASHTAGS, NO STARS.
    """
    prompt = (
        "Write a deep, poetic, and emotional title and a 1-sentence caption for a Hindi Lofi Music video. "
        "Theme: Sadness, Night, Rain, Lost Love, Silence. "
        "Style: Aesthetic, Heart touching. "
        "Language: Hinglish (Hindi + English mix). "
        "Format: TITLE | CAPTION "
        "IMPORTANT RULES: "
        "1. Do NOT use hashtags (#). "
        "2. Do NOT use asterisks (*) or bold formatting. "
        "3. Do NOT use the word 'AI' or 'Generated'. "
        "4. Keep it very clean and minimal."
    )
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.text.strip()
            
            # Extra Cleaning (Safety check)
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
    
    # Files filter
    all_videos = sorted([f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.mov'))])
    
    # History creation if missing
    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, 'w').close()
    
    with open(HISTORY_FILE, 'r') as f:
        sent_videos = f.read().splitlines()

    for video in all_videos:
        if video not in sent_videos:
            return video
    return None

def send_daily_post(video_name):
    video_path = os.path.join(VIDEO_DIR, video_name)
    
    # 1. Generate Content
    print("Generating Clean Lofi content...")
    title, caption = generate_clean_lofi_content()
    
    # Final Message (Bilkul Clean - No Hashtags)
    telegram_message = f"{title}\n\n{caption}"
    
    # 2. Construct Video Link for Webhook
    # Raw link format for public repo
    video_link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/{VIDEO_DIR}{video_name}"
    video_link = video_link.replace(" ", "%20") # Handle spaces in filename

    print(f"Sending: {title}")

    # 3. Send to Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        with open(video_path, 'rb') as video:
            try:
                # 'parse_mode' hata diya taaki koi formatting error na aaye
                requests.post(url, data={'chat_id': chat_id, 'caption': telegram_message}, files={'video': video})
                print("Telegram: Sent successfully.")
            except Exception as e:
                print(f"Telegram Error: {e}")

    # 4. Send to Webhook
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        try:
            payload = {
                "content": f"🎵 **New Upload**\nTitle: {title}\nLink: {video_link}"
            }
            requests.post(webhook_url, json=payload)
            print("Webhook: Sent successfully.")
        except Exception as e:
            print(f"Webhook Error: {e}")

# --- EXECUTION ---
video_to_send = get_next_video()

if video_to_send:
    print(f"Processing: {video_to_send}")
    send_daily_post(video_to_send)
    
    # Update History (No Delete Option - Sirf naam note karega)
    with open(HISTORY_FILE, 'a') as f:
        f.write(video_to_send + '\n')
else:
    print("No new videos found.")
