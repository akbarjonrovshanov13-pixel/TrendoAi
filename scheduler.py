# scheduler.py
"""
APScheduler yordamida kunlik avtomatlashtirilgan kontent generatsiyasi.
TrendoAI uchun moslashtirilgan.
Har soatda 06:00 dan 22:00 gacha post chiqaradi.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db, Post
from ai_generator import generate_post_for_seo
from telegram_poster import send_to_telegram_channel
from config import SITE_URL, TIMEZONE, CATEGORIES
import random
from datetime import datetime

# Mavzular ro'yxati — har xil kategoriyalarda
TOPICS = [
    # Texnologiya
    "2025 yilda eng mashhur texnologiya trendlari",
    "Kvant kompyuterlari: Kelajak hozirdan boshlanadi",
    "5G va 6G texnologiyalari orasidagi farq",
    "Metaverse nima va u biznesga qanday ta'sir qiladi",
    "IoT - Internet of Things: Aqlli uylar",
    "Bulutli hisoblash (Cloud Computing) asoslari",
    "Edge Computing nima va nima uchun kerak",
    "Blockchain texnologiyasi haqida hamma narsa",
    
    # Sun'iy intellekt
    "ChatGPT vs Gemini vs Claude: Taqqoslash",
    "Sun'iy intellekt ish o'rinlarini qanday o'zgartirmoqda",
    "AI yordamida kontentni avtomatlashtirish",
    "Generativ AI: Rasm va video yaratish",
    "Machine Learning asoslari boshlang'ichlar uchun",
    "AI chatbotlar biznes uchun",
    "Computer Vision va uning qo'llanilishi",
    "Natural Language Processing (NLP) nima",
    "AI Agent nima va qanday ishlaydi",
    "Gemini 2.0 yangiliklari",
    
    # Dasturlash
    "Python yordamida web scraping qilish",
    "React vs Vue vs Angular: Qaysi birini tanlash",
    "FastAPI bilan REST API yaratish",
    "Git va GitHub: Boshlang'ichlar uchun",
    "Clean Code yozish prinsiplari",
    "Docker bilan konteynerizatsiya",
    "Kubernetes asoslari",
    "TypeScript nima uchun kerak",
    "Next.js 15 yangiliklari",
    "Node.js vs Python: Backend uchun",
    "PostgreSQL vs MongoDB: Ma'lumotlar bazasi tanlash",
    
    # Telegram botlar
    "Python'da Telegram bot yaratish",
    "Telegram bot monetizatsiya qilish",
    "Aiogram kutubxonasi bilan ishlash",
    "Telegram Mini Apps yaratish",
    "Telegram bot uchun to'lov integratsiyasi",
    
    # Biznes va Startaplar
    "Startap uchun MVP yaratish strategiyasi",
    "IT freelancer sifatida ishlash",
    "Texnologiya startaplar uchun fund raising",
    "SaaS biznes modeli",
    "Product-Market Fit topish",
    
    # Kiberxavfsizlik
    "Kiberxavfsizlik asoslari: O'zingizni himoya qiling",
    "Parollarni xavfsiz saqlash usullari",
    "Phishing hujumlaridan himoyalanish",
    "VPN nima va qanday ishlaydi",
    "Ikki faktorli autentifikatsiya (2FA)",
    
    # Web Development
    "Landing page yaratish sirlari",
    "SEO optimizatsiya asoslari",
    "Progressive Web Apps (PWA)",
    "Web Performance optimizatsiya",
    "Responsive dizayn prinsiplari",
    
    # Mobile
    "Flutter vs React Native: 2025",
    "iOS vs Android dasturlash",
    "Mobile app monetizatsiya strategiyalari",
    
    # Yangi texnologiyalar
    "AR va VR texnologiyalari 2025",
    "Robototexnika sohasidagi yangiliklar",
    "Aqlli shaharlar texnologiyasi",
    "Elektromobillar va texnologiya",
    "Kosmik texnologiyalar trendlari",
]


def generate_and_publish_post():
    """
    Yangi post generatsiya qilib, bazaga saqlaydi va Telegramga yuboradi.
    """
    current_time = datetime.now().strftime('%H:%M')
    print(f"\n{'='*60}")
    print(f"🚀 TrendoAI — Post generatsiyasi boshlandi... [{current_time}]")
    print(f"{'='*60}")
    
    # Random mavzu va kategoriya tanlash
    selected_topic = random.choice(TOPICS)
    selected_category = random.choice(CATEGORIES)
    
    print(f"📌 Tanlangan mavzu: {selected_topic}")
    print(f"📂 Kategoriya: {selected_category}")
    
    with app.app_context():
        post_data = generate_post_for_seo(selected_topic)
        
        if post_data:
            # Rasm olish
            from image_fetcher import get_image_for_topic
            image_url = get_image_for_topic(selected_topic)
            print(f"🖼️ Rasm: {image_url[:50]}...")
            
            new_post = Post(
                title=post_data['title'],
                content=post_data['content'],
                topic=selected_topic,
                category=selected_category,
                keywords=post_data['keywords'],
                image_url=image_url,
                is_published=True
            )
            new_post.reading_time = new_post.calculate_reading_time()
            
            db.session.add(new_post)
            db.session.commit()
            
            new_post.slug = new_post.generate_slug()
            db.session.commit()
            
            print(f"✅ Yangi post '{new_post.title}' bazaga saqlandi.")
            
            # Telegramga rasm bilan yuborish
            from telegram_poster import send_photo_to_channel
            post_url = f"{SITE_URL}/post/{new_post.id}"
            tg_caption = f"""📝 *Yangi Maqola!*

*{new_post.title}*

🏷 Kategoriya: #{selected_category.replace(' ', '_')}
⏱ O'qish vaqti: {new_post.reading_time} daqiqa

🔗 [Maqolani o'qish]({post_url})

#TrendoAI #Texnologiya"""
            
            if send_photo_to_channel(image_url, tg_caption):
                print("✅ Telegram kanalga rasm bilan yuborildi!")
            else:
                print("⚠️ Telegram yuborishda muammo")
        else:
            print("❌ Post generatsiya qilishda xatolik yuz berdi.")
    
    print(f"{'='*60}\n")


# Scheduler yaratish
scheduler = BackgroundScheduler(timezone=TIMEZONE)

# Har soatda 06:00 dan 22:00 gacha post chiqarish
# 17 ta soat = 17 ta post kuniga
for hour in range(6, 23):  # 6, 7, 8... 22
    scheduler.add_job(
        generate_and_publish_post, 
        'cron', 
        hour=hour, 
        minute=0,
        id=f'hourly_post_{hour}',
        name=f'TrendoAI Soatlik Post ({hour}:00)'
    )

print(f"📅 Scheduler sozlandi: Har kuni 06:00 - 22:00 oralig'ida 17 ta post")


def get_scheduled_jobs():
    """Barcha rejalashtirilgan vazifalarni qaytaradi."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': str(job.next_run_time)
        })
    return jobs


if __name__ == "__main__":
    scheduler.start()
    print("🚀 TrendoAI Scheduler ishga tushdi!")
    print(f"📊 Jami vazifalar: {len(scheduler.get_jobs())}")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler to'xtatildi.")