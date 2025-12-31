# scheduler.py
"""
APScheduler yordamida kunlik avtomatlashtirilgan kontent generatsiyasi.
TrendoAI uchun moslashtirilgan.
Har soatda 06:00 dan 22:00 gacha post chiqaradi.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from ai_generator import generate_post_for_seo
from telegram_poster import send_to_telegram_channel
from config import SITE_URL, TIMEZONE, CATEGORIES
import random
from datetime import datetime

# 80/20 QOIDASI BO'YICHA MAVZULAR
# 80% - Mijozga qiymat beradigan foydali ma'lumotlar
# 20% - Xizmatlarimiz haqida yengil eslatmalar

TOPICS = [
    # ============ WEB SAYTLAR (80% QIYMAT) ============
    # Landing Page va Konversiya
    "Landing page yaratishda 7 ta muhim element: Konversiyani oshirish sirlari",
    "Veb-sayt tezligini 2 barobar oshirish usullari: Google Core Web Vitals",
    "Responsive dizayn: Mobil qurilmalar uchun sayt optimizatsiyasi",
    "Veb-saytda SEO optimizatsiya: Google'da birinchi o'ringa chiqish yo'llari",
    "E-commerce sayt yaratish: Online do'kon uchun to'liq qo'llanma",
    "WordPress vs Custom sayt: Qaysi birini tanlash kerak?",
    "Veb-sayt xavfsizligi: SSL, HTTPS va himoya usullari",
    "Contact forma yaratish: Mijozlarni yo'qotmaslik sirlari",
    "Veb-saytda A/B testing: Konversiyani 50% oshirish",
    "Single Page Application (SPA) nima va qachon kerak?",
    
    # ============ TELEGRAM BOTLAR (80% QIYMAT) ============
    # Bot yaratish va funksiyalar
    "Telegram bot yaratish: Boshlang'ichlar uchun to'liq qo'llanma 2025",
    "Telegram botda to'lov qabul qilish: Click, Payme, Uzcard integratsiyasi",
    "Telegram Mini App yaratish: Web ilovalarni botga ulash",
    "Aiogram 3.0 bilan professional bot yaratish",
    "Telegram bot orqali avtomatik xabar yuborish: Marketing strategiyasi",
    "Telegram kanal va guruh uchun admin bot yaratish",
    "Telegram botda inline tugmalar: Foydalanuvchi tajribasini yaxshilash",
    "CRM bot yaratish: Mijozlarni boshqarish avtomatlashtirish",
    "Telegram botda webhook vs polling: Qaysi biri yaxshi?",
    "Bot monetizatsiya: Telegram bot orqali pul ishlash yo'llari",
    
    # ============ AI CHATBOTLAR (80% QIYMAT) ============
    # Chatbot yaratish va qo'llash
    "AI chatbot nima: Biznes uchun sun'iy intellekt yordamchisi",
    "ChatGPT API bilan o'zbek tilida chatbot yaratish",
    "Mijozlarga 24/7 xizmat ko'rsatuvchi AI chatbot",
    "AI chatbot vs oddiy bot: Farqlari va afzalliklari",
    "Chatbot orqali sotuvni 3 barobar oshirish strategiyasi",
    "Gemini API bilan aqlli chatbot integratsiyasi",
    "AI chatbot uchun to'g'ri prompt yozish san'ati",
    "Chatbotda NLP: Tabiiy tilni qayta ishlash asoslari",
    "Voice chatbot: Ovozli AI yordamchi yaratish",
    "Chatbot analytics: Samaradorlikni o'lchash va yaxshilash",
    
    # ============ AVTOMATLASHTIRISH (80% QIYMAT) ============
    # Biznes jarayonlarini avtomatlashtirish
    "Biznes avtomatlashtirish: Vaqt va pulni tejash yo'llari",
    "Zapier alternativlari: Make, n8n, va bepul variantlar",
    "Email marketing avtomatlashtirish: Drip kampaniyalar",
    "CRM avtomatlashtirish: Mijoz bilan ishlashni soddalashtirish",
    "Social media avtomatlashtirish: Content scheduling tools",
    "Invoice va hisob-faktura avtomatlashtirish",
    "HR jarayonlarini avtomatlashtirish: Ishga qabul va onboarding",
    "Avtomatik hisobot yaratish: Google Sheets va API integratsiya",
    "Webhook va API orqali ilovalarni bog'lash",
    "No-code avtomatlashtirish: Dasturlashsiz yechimlar",
    
    # ============ AMALIY QIYMAT (Case Studies) ============
    "Kichik biznes uchun Telegram bot: Real natijalar",
    "Online do'kon uchun chatbot: Savdo 200% oshdi",
    "Avtomatlashtirish bilan oyiga 40 soat tejash",
    "Landing page + bot = Konversiya 5 barobarga ko'tarildi",
    "AI chatbot mijoz xizmatida: 90% so'rovlar avtomatik javob",
    
    # ============ TEXNIK YO'RIQNOMALAR ============
    "Python bilan Telegram bot: Kod misollari",
    "Next.js bilan zamonaviy sayt yaratish",
    "FastAPI + Telegram bot integratsiyasi",
    "Docker bilan bot deploy qilish: Render, Railway",
    "PostgreSQL ma'lumotlar bazasi: Bot uchun saqlash",
    
    # ============ TRENDLAR VA YANGILIKLAR ============
    "2025 yil web development trendlari",
    "Telegram Bot API yangiliklari 2025",
    "AI chatbot trendlari: Gemini 2.0, GPT-5",
    "O'zbekistonda IT xizmatlar bozori",
    "Freelance dasturchilar uchun imkoniyatlar",
]


def generate_and_publish_post(topic=None, category=None):
    """
    Yangi post generatsiya qilib, bazaga saqlaydi va Telegramga yuboradi.
    
    topic: Agar berilsa, ushbu mavzuda yozadi. Aks holda random tanlaydi.
    category: Agar berilsa, ushbu kategoriyani qo'yadi. Aks holda random tanlaydi.
    """
    current_time = datetime.now().strftime('%H:%M')
    print(f"\n{'='*60}")
    print(f"🚀 TrendoAI — Post generatsiyasi boshlandi... [{current_time}]")
    print(f"{'='*60}")
    
    # Mavzu va kategoriya tanlash
    selected_topic = topic if topic else random.choice(TOPICS)
    selected_category = category if category else random.choice(CATEGORIES)
    
    print(f"📌 Mavzu: {selected_topic}")
    print(f"📂 Kategoriya: {selected_category}")
    
    from app import app, db, Post
    with app.app_context():
        try:
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
                
                # Telegramga yuborish
                from telegram_poster import send_photo_to_channel, send_to_telegram_channel
                
                # Markdown maxsus belgilarni escape qilish
                def escape_md(text):
                    if not text: return text
                    # Escape characters that have special meaning in Markdown V2
                    # _, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., !
                    # We only escape those that are likely to appear in titles/categories
                    # and would cause formatting issues.
                    for char in ['_', '*', '[', ']', '`', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                        text = text.replace(char, '\\' + char)
                    return text
                
                post_url = f"{SITE_URL}/post/{new_post.id}"
                safe_title = escape_md(new_post.title)
                safe_category = escape_md(selected_category.replace(' ', '_')) # Replace spaces then escape
                
                tg_caption = f"""📝 *Yangi Maqola!*
    
*{safe_title}*
    
🏷 Kategoriya: #{safe_category}
⏱ O'qish vaqti: {new_post.reading_time} daqiqa
    
🔗 [Maqolani o'qish]({post_url})
    
#TrendoAI #Texnologiya"""
                
                # Rasm bilan yoki rasmsiz yuborish
                success = False
                if image_url:
                    success = send_photo_to_channel(image_url, tg_caption)
                else:
                    success = send_to_telegram_channel(tg_caption)
                
                if success:
                    print("✅ Telegram kanalga yuborildi!")
                else:
                    print("⚠️ Telegram yuborishda muammo yuz berdi")
                    
                return True
            else:
                print("❌ Post generatsiya qilishda xatolik yuz berdi (AI javob bermadi).")
                return False
        except Exception as e:
            print(f"❌ Xato yuz berdi: {str(e)}")
            return False
    
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