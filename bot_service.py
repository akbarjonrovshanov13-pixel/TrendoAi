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
Sen TrendoAI kompaniyasining professional AI assistentisan.
Isming: TrendoBot.
Vazifang: Foydalanuvchilarga texnologiya, AI, dasturlash va TrendoAI xizmatlari haqida to'liq va tushunarli javoblar berish.
Muloqot tili: O'zbek tili (Lotin yozuvi).

MUHIM QOIDALAR:
1. Javoblaringni BATAFSIL va TUSHUNARLI yoz - qisqa emas!
2. Har doim misollar va tushuntirishlar bilan javob ber.
3. Agar dasturlash savoli bo'lsa - kod misoli bilan javob ber.
4. Agar TrendoAI xizmatlari haqida so'rashsa - to'liq ma'lumot ber.
5. Savol noaniq bo'lsa - aniqlashtirish so'ra.
6. Javobni strukturali qil: raqamlar, punktlar, sarlavhalar ishlat.

TRENDOAI HAQIDA:
- Kompaniya: TrendoAI - O'zbekistondagi texnologiya va AI yechimlari kompaniyasi
- Sayt: trendoai.uz
- Telegram: @TrendoAibot
- Rahbar: Akbarjon

XIZMATLAR VA NARXLAR:
1. Telegram Botlar - $100 dan
2. Web Saytlar - $150 dan
3. AI Chatbotlar - $200 dan
4. Mini App ishlab chiqish - $300 dan
5. SMM va Marketing - $50/oy dan

MUHIM KONTEKST:
- Bugungi sana: 2025-yil dekabr
- Eng so'nggi AI modellari: Google Gemini 2.5 Flash, OpenAI GPT-4o, Claude 3.5 Sonnet
- Sen bu yangiliklardan xabardorsan

Esla: Javoblar BATAFSIL, TUSHUNARLI va FOYDALI bo'lsin!
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
🔥 **Assalomu alaykum!** Men TrendoAI assistentiman.

🤖 **Men sizga yordam bera olaman:**
• Sun'iy intellekt va AI haqida savollar
• Dasturlash va kod yozish
• Web sayt, Telegram bot buyurtma berish
• Texnologiya yangiliklari

📱 **Quyidagi tugmalardan foydalaning:**
🌐 Mini App - Saytni Telegramda oching
📋 Xizmatlar - Narxlar va xizmatlar ro'yxati

💬 Yoki savolingizni yozing, men javob beraman! 🚀
    """
    
    # Create inline keyboard with Mini App button
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # Mini App button
    web_app = telebot.types.WebAppInfo(url="https://trendoai.uz")
    mini_app_btn = telebot.types.InlineKeyboardButton(
        text="🌐 Mini App", 
        web_app=web_app
    )
    
    # Other buttons
    services_btn = telebot.types.InlineKeyboardButton(
        text="📋 Xizmatlar", 
        callback_data="services"
    )
    site_btn = telebot.types.InlineKeyboardButton(
        text="🔗 Saytga o'tish", 
        url="https://trendoai.uz"
    )
    order_btn = telebot.types.InlineKeyboardButton(
        text="🚀 Buyurtma berish", 
        url="https://trendoai.uz/order"
    )
    
    markup.add(mini_app_btn, services_btn)
    markup.add(site_btn, order_btn)
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)


# Callback handler for inline buttons
@bot.callback_query_handler(func=lambda call: call.data == "services")
def callback_services(call):
    services_text = """
🚀 **TrendoAI Xizmatlari va Narxlar:**

1. 📱 **Telegram Botlar** - $100 dan
   • Savdo botlar, To'lov integratsiya
   • Mini App ishlab chiqish

2. 🌐 **Web Saytlar** - $150 dan
   • Landing page, Korporativ saytlar
   • SEO optimizatsiya

3. 🧠 **AI Chatbotlar** - $200 dan
   • 24/7 mijozlar xizmati
   • Avtomatik javob berish

4. 📢 **SMM Marketing** - $50/oy dan
   • Kontent yaratish
   • Reklamalarni boshqarish

📞 Bog'lanish: @rovshanov_me
🌐 Sayt: trendoai.uz
    """
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, services_text, parse_mode='Markdown')


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
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
        except Exception as e:
            print(f"❌ Webhook Error: {e}")
            return 'Error', 500
    return 'Bad Request', 400

def setup_webhook(app):
    """Webhook ni sozlash (app start da chaqiriladi)"""
    # Register blueprint
    app.register_blueprint(bot_blueprint)
    
    # Set webhook URL
    webhook_url = f"{SITE_URL}/webhook"
    
    def _set_hook():
        import time
        time.sleep(1) # Wait for app to fully start
        try:
            # Eski webhook ni o'chirish
            bot.remove_webhook()
            time.sleep(0.5)
            
            # Yangi webhook o'rnatish
            bot.set_webhook(url=webhook_url)
            print(f"✅ Webhook o'rnatildi: {webhook_url}")
        except Exception as e:
            print(f"⚠️ Webhook o'rnatishda xatolik: {e}")

    # Run in background thread to not block startup
    import threading
    threading.Thread(target=_set_hook, daemon=True).start()
