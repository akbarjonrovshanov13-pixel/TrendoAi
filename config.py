# config.py
"""
TrendoAI uchun markazlashtirilgan konfiguratsiya fayli.
Barcha muhim sozlamalar shu yerda saqlanadi.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========== MUHIT SOZLAMALARI ==========
ENV = os.getenv("FLASK_ENV", "development")
DEBUG = ENV == "development"

# ========== SAYT SOZLAMALARI ==========
# Render da SITE_URL env o'zgaruvchisini ishlatish
SITE_URL = os.getenv("SITE_URL", "https://trendoai.onrender.com")

SITE_NAME = "TrendoAI"
SITE_DESCRIPTION = "O'zbekistonda trending texnologiya yangiliklari va AI-powered blog"
SITE_TAGLINE = "Trending texnologiyalar, sun'iy intellekt va biznes yangiliklari"

# ========== MA'LUMOTLAR BAZASI ==========
# ========== MA'LUMOTLAR BAZASI ==========
DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///blog.db")
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

# ========== AI SOZLAMALARI ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_MODEL_BACKUP = os.getenv("GEMINI_MODEL_BACKUP", "gemini-2.0-flash")
AI_RETRY_ATTEMPTS = 3
AI_RETRY_DELAY = 2

# ========== TELEGRAM SOZLAMALARI ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")
TELEGRAM_MAX_MESSAGE_LENGTH = 4096
TELEGRAM_RETRY_ATTEMPTS = 3

# ========== ADMIN SOZLAMALARI ==========
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "trendoai2025")
SECRET_KEY = os.getenv("SECRET_KEY", "trendoai-secret-key-change-in-production")

# ========== SCHEDULER SOZLAMALARI ==========
TIMEZONE = "Asia/Tashkent"
SEO_POST_HOUR = 9
SEO_POST_MINUTE = 0
MARKETING_POST_HOUR = 12
MARKETING_POST_MINUTE = 0

# ========== CRON SOZLAMALARI ==========
# Tashqi cron xizmatlari uchun secret key
CRON_SECRET = os.getenv("CRON_SECRET", "trendoai-cron-secret-2025")

# ========== ANALYTICS & REMARKETING ==========
# Google Analytics 4 (G-XXXXXXXXXX formatida)
GA4_ID = os.getenv("GA4_ID")
# Google Ads Remarketing (AW-XXXXXXXXXX formatida)
GOOGLE_ADS_ID = os.getenv("GOOGLE_ADS_ID")
# Facebook Pixel ID (faqat raqamlar)
FACEBOOK_PIXEL_ID = os.getenv("FACEBOOK_PIXEL_ID")

# ========== PAGINATION ==========
POSTS_PER_PAGE = 10

# ========== KATEGORIYALAR ==========
CATEGORIES = [
    "Web Saytlar",
    "Telegram Botlar", 
    "AI Chatbotlar",
    "Avtomatlashtirish",
    "Case Studies",
    "Texnik Yo'riqnomalar"
]
