# 🔥 TrendoAI — AI-Powered Trending Tech Blog

O'zbekistonda trending texnologiya yangiliklari va sun'iy intellekt haqida professional blog platformasi.

![TrendoAI](https://img.shields.io/badge/TrendoAI-v2.0-667eea?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google)

## ✨ Xususiyatlar

- 🤖 **AI-Powered Kontent** — Gemini AI yordamida avtomatik SEO-optimallashtirilgan maqolalar
- 📱 **Telegram Integratsiya** — Yangi maqolalarni avtomatik kanalga yuborish
- 🔍 **Qidiruv** — Maqolalarni sarlavha, kontent va kalit so'zlar bo'yicha qidirish
- 📂 **Kategoriyalar** — 8 ta texnologiya kategoriyasi
- 👨‍💼 **Admin Panel** — To'liq boshqaruv: postlar, generatsiya, statistika
- 🌐 **SEO** — Meta taglar, Open Graph, Sitemap, Robots.txt
- 📊 **API** — RESTful API endpoints
- 🐳 **Docker Ready** — Render.com va boshqa platformalarga deploy

## 🛠️ Texnologiyalar

| Texnologiya | Versiya | Vazifasi |
|------------|---------|----------|
| Flask | 3.0.3 | Web framework |
| SQLAlchemy | 3.1.1 | ORM / Database |
| Gemini AI | Flash | Kontent generatsiyasi |
| APScheduler | 3.10.4 | Cron jobs |
| Gunicorn | 21.2.0 | Production server |

## 📦 O'rnatish

### 1. Repozitoriyani klonlash
```bash
git clone https://github.com/your-username/trendoai.git
cd trendoai
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlash
```env
# Gemini API (Google AI Studio'dan oling)
GEMINI_API_KEY=your_api_key_here

# Telegram (@BotFather dan oling)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_name

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Production uchun
SECRET_KEY=your-secret-key-here
SITE_URL=https://your-domain.com
FLASK_ENV=production
```

### 5. Ilovani ishga tushirish
```bash
# Development
python app.py

# Production
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🌐 Sahifalar

| URL | Tavsif |
|-----|--------|
| `/` | Bosh sahifa — barcha maqolalar |
| `/post/<id>` | Bitta maqola sahifasi |
| `/search?q=...` | Qidiruv natijalari |
| `/about` | Biz haqimizda |
| `/services` | Xizmatlar |
| `/admin` | Admin panel (login kerak) |

## 🔌 API Endpoints

| Endpoint | Method | Tavsif |
|----------|--------|--------|
| `/api/health` | GET | Health check |
| `/api/posts` | GET | Barcha postlar (pagination) |
| `/api/posts/<id>` | GET | Bitta post |
| `/api/stats` | GET | Statistika |
| `/sitemap.xml` | GET | SEO sitemap |
| `/robots.txt` | GET | Robots file |

## ⏰ Avtomatlashtirish Jadvali

| Vaqt (Toshkent) | Vazifa |
|-----------------|--------|
| 09:00 | SEO blog maqolasi generatsiyasi |
| 12:00 | Marketing posti Telegramga |

## 🚀 Render.com Deploy

1. [Render.com](https://render.com) da yangi Web Service yarating
2. GitHub repo'ni ulang
3. Environment variables qo'shing:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHANNEL_ID`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `SITE_URL` (masalan: `https://trendoai.onrender.com`)
4. Deploy tugmasini bosing

## 📁 Loyiha Strukturasi

```
trendoai/
├── app.py              # Flask main + routes + API
├── config.py           # Configuration
├── ai_generator.py     # Gemini AI integration
├── scheduler.py        # APScheduler jobs
├── telegram_poster.py  # Telegram API
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker build
├── render.yaml         # Render.com config
├── .env               # Environment (gitignore)
├── .gitignore
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── search.html
│   ├── about.html
│   ├── services.html
│   ├── admin/
│   │   ├── base_admin.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── posts.html
│   │   ├── edit_post.html
│   │   └── generate.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── instance/
    └── blog.db
```

## 📞 Aloqa

- 🌐 **Sayt**: [trendoai.uz](https://trendoai.uz)
- 📱 **Telegram**: [@trendoai](https://t.me/trendoai)
- 📧 **Email**: info@trendoai.uz

## 📄 Litsenziya

MIT License © 2025 TrendoAI
