import telebot
import google.generativeai as genai
from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, GEMINI_MODEL, SITE_URL
from datetime import datetime
from flask import request, Blueprint

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# Create bot instance
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Create Blueprint for webhook
bot_blueprint = Blueprint('bot', __name__)

SYSTEM_PROMPT = """
Sen TrendoAI loyihasining professional AI assistentisan.
Isming: TrendoBot.
Vazifang: Foydalanuvchilarga texnologiya, AI, dasturlash va TrendoAI xizmatlari haqida yordam berish.
Muloqot tili: O'zbek tili (Lotin yozuvi).
Xususiyatlaring:
1. Muloyim va professional.
2. Javoblaring aniq va lo'nda.
3. Agar TrendoAI xizmatlari haqida so'rashsa (Web sayt, Bot, SMM), ularga /services buyrug'ini tavsiya qil.
4. Kod yozishda yordam berasan.

Sayt: trendoai.uz

MUHIM KONTEKST (Roleplay):
- Bugun: 2025-yil dekabr.
- Eng so'nggi AI modellari: Google Gemini 3.0 Pro, Gemini 2.5 Flash, OpenAI GPT-5.
- Sen shu yangiliklardan xabardorsan va ular haqida bemalol gaplasha olasan.
"""

def get_ai_response(user_message):
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        dynamic_prompt = f"{SYSTEM_PROMPT}\nBugungi sana: {current_date}"
        
        chat = model.start_chat(history=[
            {"role": "user", "parts": [dynamic_prompt]}
        ])
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        print(f"❌ Gemini AI Error: {e}")
        return "Uzr, hozirda serverda xatolik yuz berdi. Birozdan so'ng urinib ko'ring."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
👋 **Assalomu alaykum!** Men TrendoAI assistentiman.

Men sizga quyidagi masalalarda yordam bera olaman:
🔹 Sun'iy intellekt va Texnologiyalar
🔹 Dasturlash bo'yicha savollar
🔹 TrendoAI xizmatlari haqida ma'lumot

Savolingizni yozing, men javob berishga tayyorman! 🚀
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['services'])
def send_services(message):
    services_text = """
🚀 **TrendoAI Xizmatlari:**

1. **Telegram Botlar:** Biznesingiz uchun mukammal botlar.
2. **Web Saytlar:** Zamonaviy va tezkor saytlar.
3. **AI Integratsiya:** Ish jarayonlarini avtomatlashtirish.
4. **SMM Dizayn:** Brendingizni rivojlantirish.

Buyurtma berish uchun saytimizga o'ting: trendoai.uz/services
Yoki menga "Web sayt kerak" deb yozing.
    """
    bot.reply_to(message, services_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_chat_action(message.chat.id, 'typing')
    ai_reply = get_ai_response(message.text)
    
    try:
        bot.reply_to(message, ai_reply, parse_mode='Markdown')
    except Exception as e:
        try:
            bot.reply_to(message, ai_reply, parse_mode=None)
        except Exception as e2:
            bot.reply_to(message, "Uzr, xatolik yuz berdi.")

# ========== WEBHOOK ENDPOINT ==========
@bot_blueprint.route('/webhook', methods=['POST'])
def webhook():
    """Telegram Webhook endpoint"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Bad Request', 400

def setup_webhook(app):
    """Webhook ni sozlash (app start da chaqiriladi)"""
    # Register blueprint
    app.register_blueprint(bot_blueprint)
    
    # Set webhook URL
    webhook_url = f"{SITE_URL}/webhook"
    
    try:
        # Eski webhook ni o'chirish
        bot.remove_webhook()
        
        # Yangi webhook o'rnatish
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook o'rnatildi: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Webhook xatosi: {e}")
