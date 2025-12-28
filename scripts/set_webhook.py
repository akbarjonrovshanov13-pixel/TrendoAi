import os
import time
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Default to render URL if not set, but print warning
SITE_URL = os.getenv("SITE_URL", "https://trendoai.onrender.com")

if not TELEGRAM_BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables")
    exit(1)

print(f"🔄 Setting up webhook for bot...")
print(f"📍 Site URL: {SITE_URL}")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def set_webhook_manual():
    webhook_url = f"{SITE_URL}/webhook"
    try:
        # Remove previous webhook
        print("1️⃣ Removing old webhook...")
        bot.remove_webhook()
        time.sleep(1)
        
        # Set new webhook
        print(f"2️⃣ Setting new webhook to: {webhook_url}")
        bot.set_webhook(url=webhook_url)
        
        # Verify
        print("3️⃣ Verifying webhook info...")
        info = bot.get_webhook_info()
        print(f"✅ Success! Webhook url: {info.url}")
        print(f"ℹ️ Pending updates: {info.pending_update_count}")
        
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")

if __name__ == "__main__":
    set_webhook_manual()
