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

# Modelni yaratish
model = genai.GenerativeModel(GEMINI_MODEL)


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
    Siz TrendoAI uchun professional maqola yozuvchisiz.
    
    MUHIM: Bugun 2025-yil dekabr oyi. Maqolani 2025-yil dekabr holatiga nisbatan yozing.
    Eng so'nggi texnologiyalar, trendlar va yangiliklar haqida yozing.
    Eski ma'lumotlar emas, faqat 2024-2025 yildagi yangiliklar bo'lsin.
    
    Vazifa: "{topic}" mavzusi bo'yicha professional maqola yozing.
    
    MUHIM TALABLAR:
    1. O'zbek tilida (lotin alifbosi) yozing
    2. Kamida 500 so'z bo'lsin
    3. 2025-yil dekabr holatidagi eng so'nggi ma'lumotlar
    4. FAQAT Markdown formatlash ishlating:
       - ## va ### sarlavhalar
       - **qalin** matn
       - - yoki * bilan ro'yxatlar
       - 1. 2. 3. raqamli ro'yxatlar
    5. HTML teglarni ISHLATMANG (</p>, <h2>, <strong> va h.k.)
    6. Strukturasi: Kirish, 3-4 bo'lim, Xulosa
    
    JSON formatida javob bering:
    {{
      "title": "Qisqa, qiziqarli sarlavha (50-60 belgi)",
      "keywords": "kalit1, kalit2, kalit3, kalit4, kalit5",
      "content": "Markdown formatidagi toza maqola matni"
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