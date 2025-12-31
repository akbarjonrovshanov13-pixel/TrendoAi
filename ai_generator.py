# ai_generator.py
"""
Gemini AI yordamida SEO-optimallashtirilgan kontent generatsiya qilish moduli.
TrendoAI uchun moslashtirilgan.
Zaxira API kalit va model bilan fallback qo'llab-quvvatlash.
"""
import os
import json
import re
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODEL_BACKUP, AI_RETRY_ATTEMPTS, AI_RETRY_DELAY

# Zaxira API kalit
GEMINI_API_KEY2 = os.getenv("GEMINI_API_KEY2")

# Hozirgi faol API kalit va model
current_api_key = GEMINI_API_KEY
current_model_name = GEMINI_MODEL

def _configure_api(api_key):
    """API kalitni sozlash"""
    global current_api_key
    if api_key:
        genai.configure(api_key=api_key)
        current_api_key = api_key
        return True
    return False

def _switch_to_backup():
    """Zaxira API kalitga yoki modelga o'tish"""
    global current_api_key, current_model_name, model
    
    # Avval zaxira modelga o'tish
    if current_model_name != GEMINI_MODEL_BACKUP:
        print(f"🔄 Zaxira modelga o'tilmoqda: {GEMINI_MODEL_BACKUP}...")
        current_model_name = GEMINI_MODEL_BACKUP
        model = genai.GenerativeModel(current_model_name)
        return True
    
    # Keyin zaxira API kalitga o'tish
    if GEMINI_API_KEY2 and current_api_key != GEMINI_API_KEY2:
        print("🔄 Zaxira API kalitga o'tilmoqda (GEMINI_API_KEY2)...")
        _configure_api(GEMINI_API_KEY2)
        current_model_name = GEMINI_MODEL  # Asosiy model bilan
        model = genai.GenerativeModel(current_model_name)
        return True
    
    return False

# Dastlabki API kalitni sozlash
_configure_api(GEMINI_API_KEY)

# Google Search grounding - real internet ma'lumotlarini olish
from google.generativeai.types import Tool

google_search_tool = Tool(
    name="google_search",
    description="Search the web for current information"
)

# Modelni yaratish (Google Search grounding bilan)
model = genai.GenerativeModel(
    GEMINI_MODEL,
    tools=[google_search_tool]
)



def _retry_with_backoff(func, *args, **kwargs):
    """
    Funksiyani retry mehanizmi bilan ishga tushiradi.
    Exponential backoff: 2s, 4s, 8s
    Agar barcha urinishlar muvaffaqiyatsiz bo'lsa, zaxira model/API kalitga o'tadi.
    """
    global model
    last_exception = None
    
    for attempt in range(AI_RETRY_ATTEMPTS):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            wait_time = AI_RETRY_DELAY * (2 ** attempt)
            print(f"🔄 AI xatolik (urinish {attempt + 1}/{AI_RETRY_ATTEMPTS}): {e}")
            print(f"⏳ {wait_time} soniya kutilmoqda...")
            time.sleep(wait_time)
    
    # Asosiy model/kalit bilan muvaffaqiyatsiz - zaxiraga o'tish
    if _switch_to_backup():
        print("🔄 Zaxira sozlama bilan qayta urinilmoqda...")
        
        for attempt in range(AI_RETRY_ATTEMPTS):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = AI_RETRY_DELAY * (2 ** attempt)
                print(f"🔄 Zaxira sozlama xatolik (urinish {attempt + 1}/{AI_RETRY_ATTEMPTS}): {e}")
                time.sleep(wait_time)
        
        # Yana bir urinish - ikkinchi zaxira variantga o'tish
        if _switch_to_backup():
            print("🔄 Ikkinchi zaxira sozlama bilan urinilmoqda...")
            for attempt in range(AI_RETRY_ATTEMPTS):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    time.sleep(AI_RETRY_DELAY)
    
    print(f"❌ Barcha urinishlar muvaffaqiyatsiz. Oxirgi xato: {last_exception}")
    return None


def _parse_json_response(response_text):
    """
    AI javobidan JSON ni xavfsiz ajratib olish.
    ```json ... ``` bloklarini tozalaydi.
    """
    cleaned = response_text.strip()
    
    # JSON blokni tozalash
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse xatosi: {e}")
        # Regex orqali urinib ko'rish
        try:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
            
        print(f"📄 Raw javob: {cleaned[:200]}...")
        return None


def generate_post_for_seo(topic):
    """
    Berilgan mavzu bo'yicha SEO'ga moslashtirilgan maqola generatsiya qiladi.
    
    Args:
        topic: Maqola mavzusi
        
    Returns:
        dict: {"title": str, "keywords": str, "content": str} yoki None
    """
    prompt = f"""
    Siz TrendoAI uchun professional SEO-maqola yozuvchi ekspertisiz.
    
    === MUHIM KONTEKST (2025-YIL DEKABR) ===
    Bugun 2025-yil dekabr oyi oxiri. Real internetdan eng yangi ma'lumotlarni oling.
    Eng so'nggi texnologiyalar: GPT-5.2, Gemini 3, Claude Opus 4.5, AI Agentlar, RAG tizimlar.
    
    MUHIM: Google Search orqali mavzu haqida eng yangi ma'lumotlarni toping va ulardan foydalaning!
    
    === 80/20 QOIDASI (JUDA MUHIM!) ===
    - 80% FOYDALI MA'LUMOT: O'quvchiga haqiqiy qiymat bering
    - 20% KOMPANIYA HAQIDA: Faqat oxirida yengil eslatma
    
    Maqola oxirida shunday yozing:
    "Agar sizga ham [mavzu bo'yicha xizmat] kerak bo'lsa, TrendoAI jamoasi yordam beradi. 
    Bepul konsultatsiya uchun: t.me/Akramjon1984"
    
    === VAZIFA ===
    "{topic}" mavzusida professional maqola yozing.

    
    === SEO TALABLARI (Google/Yandex uchun - JUDA MUHIM!) ===
    
    SARLAVHA OPTIMIZATSIYASI:
    - Asosiy kalit so'z ALBATTA sarlavhada bo'lsin
    - Raqam ishlating: "7 ta usul", "2025 yilda", "5 qadam"
    - Savol yoki muammo: "Qanday qilib...", "Nima uchun...", "Eng yaxshi..."
    - Misol: "Telegram Bot Yaratish 2025: 7 ta Muhim Qadam" ✅
    - Noto'g'ri: "Bot haqida umumiy ma'lumot" ❌
    
    KALIT SO'ZLAR OPTIMIZATSIYASI:
    - 1-kalit: Asosiy qidiruv so'zi (masalan: "telegram bot yaratish")
    - 2-kalit: Boshqa variant (masalan: "telegram bot qilish")
    - 3-kalit: Texnologiya nomi (masalan: "python telegram bot")
    - 4-kalit: Muammo/yechim (masalan: "bot orqali pul ishlash")
    - 5-kalit: Mahalliy (masalan: "o'zbekistonda telegram bot")
    
    KONTENT ICHIDA SEO:
    - Birinchi 100 so'zda asosiy kalit so'z bo'lsin
    - Har bir H2/H3 sarlavhada kalit so'z variant bo'lsin
    - Kalit so'zlarni tabiiy tarzda 3-5 marta takrorlang
    - 1000-1500 so'z uzunlik (Google chuqur kontentni yaxshi ko'radi)
    
    === KONTENT TALABLARI ===
    1. O'zbek tilida (lotin alifbosi)
    2. Professional lekin tushunarli til
    3. Amaliy misollar va statistika (raqamlar bilan)
    4. FAQAT Markdown formatlash (## ### ** - 1.)
    5. HTML teglar YO'Q
    
    === STRUKTURA ===
    - **Kirish**: Muammoni tushuntiring, asosiy kalit so'z (150-200 so'z)
    - **Asosiy qism**: 4-5 bo'lim, har bir H2 da kalit so'z varianti
    - **Xulosa**: Qisqa takrorlash + TrendoAI eslatmasi (80/20)
    
    JSON formatida javob bering:
    {{
      "title": "Asosiy kalit so'z + raqam/savol sarlavha (50-65 belgi)",
      "keywords": "asosiy_kalit, variant_kalit, texnologiya, muammo_yechim, mahalliy",
      "content": "To'liq SEO-optimallashtirilgan Markdown maqola (1000-1500 so'z)"
    }}
    
    Faqat JSON qaytaring!
    """


    
    def _generate():
        response = model.generate_content(prompt)
        return _parse_json_response(response.text)
    
    result = _retry_with_backoff(_generate)
    
    if result and all(k in result for k in ['title', 'keywords', 'content']):
        return result
    
    print("⚠️ AI javobi noto'g'ri formatda")
    return None


def generate_marketing_post_for_telegram():
    """
    Mijozlarni jalb qilish uchun Telegram kanaliga marketing posti yaratadi.
    
    Returns:
        str: Marketing post matni yoki None
    """
    prompt = """
    TrendoAI — O'zbekistondagi texnologiya va sun'iy intellekt haqidagi yetakchi blog platformasi uchun Telegram kanaliga qisqa, jalb qiluvchi post yozing.
    
    TrendoAI haqida:
    - Trending texnologiya yangiliklari
    - Sun'iy intellekt va AI haqida maqolalar
    - Dasturlash bo'yicha qo'llanmalar
    - Startap va IT biznes maslahatlar
    
    Post talablari:
    - 150-200 so'z
    - Qiziqarli va professional
    - Emoji'lar ishlating
    - O'quvchilarni blogga tashrif buyurishga chaqiring
    - Harakatga chaqiruvchi tugallang
    
    Faqat post matnini yozing.
    """
    
    def _generate():
        response = model.generate_content(prompt)
        return response.text.strip()
    
    result = _retry_with_backoff(_generate)
    return result


def generate_custom_content(prompt_text):
    """
    Ixtiyoriy prompt bo'yicha kontent generatsiya qiladi.
    
    Args:
        prompt_text: AI'ga yuboriladigan prompt
        
    Returns:
        str: Generatsiya qilingan matn yoki None
    """
    def _generate():
        response = model.generate_content(prompt_text)
        return response.text.strip()
    
    return _retry_with_backoff(_generate)


def generate_portfolio_content(title, category):
    """
    Portfolio loyiha uchun AI yordamida kontent generatsiya qiladi.
    
    Args:
        title: Loyiha nomi
        category: Loyiha kategoriyasi (bot, web, ai, mobile)
        
    Returns:
        dict yoki None
    """
    category_names = {
        'bot': 'Telegram Bot',
        'web': 'Web Sayt',
        'ai': 'AI Yechim',
        'mobile': 'Mobile Ilova'
    }
    
    cat_name = category_names.get(category, category)
    
    prompt = f"""
    Siz TrendoAI uchun professional portfolio kontenti yozuvchisiz.
    
    Vazifa: "{title}" nomli {cat_name} loyihasi uchun professional marketing kontenti yarating.
    
    MUHIM TALABLAR:
    1. O'zbek tilida (lotin alifbosi) yozing
    2. Professional va ishonchli ohangda
    3. Mijozlarni jalb qiluvchi
    
    JSON formatida javob bering:
    {{
      "description": "Loyiha haqida qisqa tavsif (2-3 jumla, 100-150 belgi)",
      "technologies": "Python, Flask, PostgreSQL (3-5 ta texnologiya, vergul bilan)",
      "features": "To'lov tizimi, Admin panel, Real-time xabarlar (5-7 ta feature, vergul bilan)",
      "details": "## Loyiha haqida\\n\\nBatafsil ma'lumot markdown formatida. 150-200 so'z.",
      "meta_description": "SEO uchun meta tavsif (150-160 belgi)",
      "meta_keywords": "telegram bot, python (5-7 kalit so'z, vergul bilan)"
    }}
    
    Faqat JSON qaytaring!
    """
    
    def _generate():
        response = model.generate_content(prompt)
        return _parse_json_response(response.text)
    
    result = _retry_with_backoff(_generate)
    
    if result:
        return result
    
    print("⚠️ Portfolio AI javobi noto'g'ri formatda")
    return None


# Test uchun
if __name__ == '__main__':
    print("=" * 60)
    print("🔥 TrendoAI — AI Generator Test")
    print("=" * 60)
    
    print("\n📢 Marketing post generatsiya qilinmoqda...")
    marketing_text = generate_marketing_post_for_telegram()
    if marketing_text:
        print("✅ Muvaffaqiyatli!")
        print("-" * 40)
        print(marketing_text)
    else:
        print("❌ Xatolik yuz berdi")