# app.py
"""
TrendoAI — Trending texnologiyalar va sun'iy intellekt haqida professional blog.
Flask asosiy fayli.
"""
import os
import re
import markdown2
from datetime import datetime
from functools import wraps
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklash
load_dotenv()

app = Flask(__name__)

# Konfiguratsiya
from config import (
    SITE_URL, SITE_NAME, SITE_DESCRIPTION, DATABASE_URI, SECRET_KEY,
    ADMIN_USERNAME, ADMIN_PASSWORD, POSTS_PER_PAGE, CATEGORIES,
    GA4_ID, GOOGLE_ADS_ID, FACEBOOK_PIXEL_ID
)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)


# ========== SERVICE DATA (For Landing Pages) ==========
SERVICES_DATA = {
    'ai_content': {
        'key': 'ai_content',
        'title': 'AI Kontent Generatsiya',
        'icon': '🤖',
        'description': "Sun'iy intellekt yordamida SEO-optimallashtirilgan blog maqolalari va marketing kontentlari.",
        'features': [
            'Avtomatik blog postlar va maqolalar',
            'SEO kalit so\'zlar tahlili va integratsiyasi',
            'Telegram kanallarga avtomatik yuborish',
            'Ko\'p tilli kontent yaratish (Uz, Ru, En)'
        ],
        'price': '500,000 so\'m/oy dan',
        'full_description': "TrendoAI taklif etayotgan AI Kontent Generatsiya xizmati sizning biznesingiz uchun avtomatik, sifatli va SEO-optimallashtirilgan kontent yaratishga yordam beradi. Bizning tizim Google-ning eng so'nggi Gemini AI texnologiyasi asosida ishlaydi va o'zbek tilidagi eng mukammal, inson tomonidan yozishga o'xshash kontentni taqdim etadi.",
        'meta_desc': "AI yordamida professional blog va marketing kontentlari yaratish. TrendoAI AI-agentlari biznesingiz uchun 24/7 ishlaydi."
    },
    'telegram_bot': {
        'key': 'telegram_bot',
        'title': 'Telegram Botlar',
        'icon': '📱',
        'description': "Biznesingiz uchun murakkab funksional va foydalanuvchilarga qulay Telegram botlar.",
        'features': [
            'Telegram Mini App (Web App) yaratish',
            'To\'lov tizimlari (Click, Payme) integratsiyasi',
            'Boshqaruv paneli (Admin Panel)',
            'Mijozlar bazasi va statistika'
        ],
        'price': '1,500,000 so\'m dan',
        'full_description': "Sizning biznes jarayonlaringizni avtomatlashtirish uchun murakkab va foydali Telegram botlarni ishlab chiqamiz. Savdo botlari, mijozlarni qo'llab-quvvatlash botlari, e-commerce Mini Applar va maxsus tizimlar - barchasini TrendoAI jamoasi taqdim etadi.",
        'meta_desc': "Telegram botlar va Mini Applar ishlab chiqish. Biznesingizni Telegram orqali avtomatlashtiring va savdoni oshiring."
    },
    'web_site': {
        'key': 'web_site',
        'title': 'Web Saytlar',
        'icon': '🌐',
        'description': "Zamonaviy, o'ta tez va SEO-optimallashtirilgan professional veb-saytlar.",
        'features': [
            'Landing Page (Bir sahifali sayt)',
            'Korporativ va brend saytlari',
            'E-commerce (Internet do\'konlar)',
            'Zamonaviy UI/UX va mobil moslashuv'
        ],
        'price': '2,000,000 so\'m dan',
        'full_description': "Biz zamonaviy texnologiyalar (Next.js, React, Flask, Node.js) yordamida har qanday murakkablikdagi veb-saytlarni yaratamiz. Saytlarimiz tezligi, Google qidiruv tizimi uchun to'liq optimalligi va brendingizga mos dizayni bilan ajralib turadi.",
        'meta_desc': "Professional veb-saytlar yaratish. Landing page, korporativ saytlar va internet do'konlar. SEO va mobil adaptiv."
    },
    'ai_chatbot': {
        'key': 'ai_chatbot',
        'title': 'AI Chatbot Yaratish',
        'icon': '🧠',
        'description': "Mijozlaringizga sun'iy intellekt orqali 24/7 xizmat ko'rsatish tizimi.",
        'features': [
            'Intellektual javoblar (LLM asosida)',
            'Mavjud ma\'lumotlar bazasi bilan integratsiya',
            'Telegram, WhatsApp va Sayt uchun yagona bot',
            'Mijozlar bilan insondek muloqot'
        ],
        'price': '2,500,000 so\'m dan',
        'full_description': "Mijozlaringiz bilan kechayu-kunduz muloqot qiladigan, ularning savollariga aniq va aqlli javob beradigan AI chatbotlarni yarating. Gemini yoki ChatGPT asosidagi ushbu tizimlar xodimlar xarajatini kamaytiradi va mijozlar talabiga tezkor javob beradi.",
        'meta_desc': "Aqlli AI Chatbotlar va virtual assistentlar yaratish. Biznesingiz uchun sun'iy intellektli mijozlar xizmati."
    },
    'smm': {
        'key': 'smm',
        'title': 'SMM Avtomatlashtirish',
        'icon': '📢',
        'description': "Ijtimoiy tarmoqlar uchun AI agentlar yordamida avtomatik boshqaruv.",
        'features': [
            'Postlarni AI yordamida rejalashtirish',
            'Kreativ rasm va matnlar generatsiyasi',
            'Avtomatik ijtimoiy tarmoq tahlili',
            'Kross-platforma posting (TG, FB, IG)'
        ],
        'price': '800,000 so\'m/oy dan',
        'full_description': "Ijtimoiy tarmoqlardagi faolligingizni aqlli avtomatlashtirish orqali yanada samarali qiling. Bizning AI tizimlarimiz trendlarni kuzatadi, matn yozadi va brendingiz uchun foydali auditoriyani jalb qilishga yordam beradi.",
        'meta_desc': "AI SMM avtomatlashtirish xizmatlari. Kontent yaratish va ijtimoiy tarmoqlarni avtomatik boshqarish."
    },
    'consulting': {
        'key': 'consulting',
        'title': 'IT Konsalting',
        'icon': '💡',
        'description': "Raqamli transformatsiya va sun'iy intellektni joriy qilish bo'yicha maslahatlar.",
        'features': [
            'Biznes jarayonlarni texnik audit qilish',
            'AI texnologiyalarini rejalashtirish',
            'Dasturiy mahsulotlar arxitekturasi',
            'Top-menejment uchun texnik treninglar'
        ],
        'price': '500,000 so\'m/soat dan',
        'full_description': "Sizning g'oyangizni qanday qilib texnologiya orqali amalga oshirish yoki mavjud tizimingizni qanday optimallashtirish bo'yicha professional maslahat beramiz. AI asrida biznesingizni yangi bosqichga olib chiqishda yo'l ko'rsatamiz.",
        'meta_desc': "Professional IT konsalting va AI audit xizmatlari. Biznesingizni raqamli transformatsiya qiling."
    },
    'crm_integration': {
        'key': 'crm_integration',
        'title': 'CRM Integratsiya',
        'icon': '⚙️',
        'description': "Sotuv jarayonlarini avtomatlashtirish va mijozlar bazasini tartibga solish.",
        'features': [
            'AmoCRM / Bitrix24 integratsiyasi',
            'Telegram botdan CRM ga lidlar tushishi',
            'Sotuv voronkalarini avtomatlashtirish',
            'Menejerlar faoliyatini nazorat qilish'
        ],
        'price': '2,000,000 so\'m',
        'discount': {
            'percent': 30,
            'until': '1-fevral'
        },
        'full_description': "Biznesingizda tartib o'rnating! Buyurtmalarni Excel yoki daftarda emas, zamonaviy CRM tizimlarida yuriting. Biz sizning Telegram botingiz, saytingiz va Instagram sahifangizni yagona CRM bazasiga ulab beramiz. Har bir mijoz nazoratda bo'ladi.",
        'meta_desc': "CRM tizimlarini (AmoCRM, Bitrix24) joriy qilish va integratsiya xizmatlari. Biznes jarayonlarni avtomatlashtirish."
    },
    'voice_ai': {
        'key': 'voice_ai',
        'title': 'AI Ovozli Assistent',
        'icon': '📞',
        'description': "Call-markazlar o'rniga sun'iy intellekt asosidagi aqlli ovozli operatorlar.",
        'features': [
            'Kiruvchi qo\'ng\'iroqlarga javob berish',
            'Mijozlarga avtomatik qo\'ng\'iroq qilish (Cold calling)',
            'Inson ovozidan farq qilmaydigan muloqot',
            '24/7 ish tartibi'
        ],
        'price': '3,000,000 so\'m dan',
        'discount': {
            'percent': 30,
            'until': '1-fevral'
        },
        'full_description': "Endi katta call-markaz ushlash shart emas. Bizning AI ovozli assistentlarimiz mijozlaringiz bilan xuddi insondek gaplashadi, savollarga javob beradi va buyurtma qabul qiladi. Bu xarajatlarni 70% ga qisqartiradi.",
        'meta_desc': "AI ovozli assistentlar va virtual call-markaz xizmatlari. Sun'iy intellekt orqali mijozlar bilan ovozli muloqot."
    },
    'marketplace_auto': {
        'key': 'marketplace_auto',
        'title': 'Marketpleys Avtomatlashtirish',
        'icon': '🛍️',
        'description': "Uzum va Wildberries da savdo qiluvchilar uchun maxsus botlar va dasturlar.",
        'features': [
            'Tovarlarni avtomatik yuklash',
            'Raqobatchilar narxini kuzatish',
            'Sotuvlar analitikasi (Bot orqali)',
            'Ombor qoldiqlarini boshqarish'
        ],
        'price': '1,500,000 so\'m',
        'discount': {
            'percent': 30,
            'until': '1-fevral'
        },
        'full_description': "E-tijoratda vaqt bu pul. Uzum Market yoki Wildberries do'koningizni boshqarishni avtomatlashtiring. Bizning yechimlarimiz orqali siz narxlarni tezkor o'zgartirishingiz va kunlik foydani telefoningizdan kuzatib borishingiz mumkin.",
        'meta_desc': "Uzum va Wildberries marketpleyslari uchun avtomatlashtirish xizmatlari. Savdoni oshirish uchun maxsus dasturlar."
    },
    'data_analytics': {
        'key': 'data_analytics',
        'title': 'Data Analitika',
        'icon': '📊',
        'description': "Biznes ko'rsatkichlarini real vaqtda kuzatib borish uchun Dashboardlar.",
        'features': [
            'Sotuv va xarajatlar Dashboardi',
            'Telegram orqali kunlik hisobotlar',
            'Power BI / Google Data Studio integratsiyasi',
            'Marketing samaradorligi tahlili'
        ],
        'price': '2,500,000 so\'m',
        'discount': {
            'percent': 30,
            'until': '1-fevral'
        },
        'full_description': "Raqamlarga asoslanib qaror qabul qiling. Biz sizning barcha ma'lumotlaringizni (Excel, CRM, 1C) yagona tushunarli Dashboardga yig'ib beramiz. Endi biznesingiz holatini bir qarashda tushunasiz.",
        'meta_desc': "Biznes uchun Data Analitika va Dashboardlar yaratish. Power BI va Google Data Studio xizmatlari."
    },
    'ai_education': {
        'key': 'ai_education',
        'title': 'AI Ta\'lim (Korporativ)',
        'icon': '🎓',
        'description': "Xodimlaringizga sun'iy intellekt (ChatGPT, Midjourney) dan foydalanishni o'rgatamiz.",
        'features': [
            'Prompt Engineering asoslari',
            'Ish jarayonida AI dan foydalanish',
            'Marketing va SMM uchun AI',
            'Amaliy master-klasslar'
        ],
        'price': '1,000,000 so\'m (guruh)',
        'discount': {
            'percent': 30,
            'until': '1-fevral'
        },
        'full_description': "Raqobatchilardan oldinda bo'ling! Xodimlaringizga sun'iy intellektdan foydalanishni o'rgating va ish samaradorligini 10 barobar oshiring. Biz har bir soha (sotuv, marketing, HR) uchun maxsus o'quv dasturlarini taklif qilamiz.",
        'meta_desc': "Sun'iy intellekt (AI) bo'yicha korporativ treninglar va kurslar. ChatGPT va Midjourney dan foydalanishni o'rganing."
    }
}


# ========== DATABASE MODELS ==========

class Post(db.Model):
    """Blog post modeli"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=True)
    content = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Texnologiya')
    keywords = db.Column(db.String(250), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    views = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer, default=5)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f'<Post {self.title}>'
    
    def calculate_reading_time(self):
        """O'qish vaqtini hisoblash (250 so'z/daqiqa)"""
        word_count = len(self.content.split())
        return max(1, round(word_count / 250))
    
    def generate_slug(self):
        """URL uchun slug yaratish"""
        slug = self.title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return f"{slug}-{self.id}"
    
    def to_dict(self):
        """API uchun dict formatiga o'tkazish"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'topic': self.topic,
            'category': self.category,
            'keywords': self.keywords,
            'views': self.views,
            'reading_time': self.reading_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Order(db.Model):
    """Xizmatga buyurtma modeli"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='new')  # new, contacted, completed, cancelled
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Order {self.id} - {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'service': self.service,
            'service_name': self.service_name,
            'budget': self.budget,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Portfolio(db.Model):
    """Portfolio loyihalar modeli (SEO-optimized)"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=True)  # SEO URL
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='web')  # bot, web, ai, mobile
    emoji = db.Column(db.String(10), default='🚀')
    technologies = db.Column(db.String(250))  # vergul bilan ajratilgan
    link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))  # Rasm URL
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    # SEO fields
    meta_description = db.Column(db.String(160))  # SEO tavsifi
    meta_keywords = db.Column(db.String(250))  # SEO kalit so'zlar
    details = db.Column(db.Text)  # Batafsil ma'lumot (Markdown)
    features = db.Column(db.Text)  # Loyiha imkoniyatlari (vergul bilan ajratilgan)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Portfolio {self.title}>'
    
    def generate_slug(self):
        """URL uchun slug yaratish"""
        slug = self.title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return f"{slug}-{self.id}"
    
    def to_dict(self):
        # Use getattr for new columns to handle missing DB columns gracefully
        details = getattr(self, 'details', None) or ''
        features = getattr(self, 'features', None) or ''
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'emoji': self.emoji,
            'technologies': self.technologies.split(',') if self.technologies else [],
            'link': self.link,
            'image_url': self.image_url,
            'is_featured': self.is_featured,
            'details': details,
            'details_html': markdown2.markdown(details) if details else "",
            'features': features.split(',') if features else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ========== TEMPLATE FILTERS ==========

@app.template_filter('markdown')
def markdown_filter(s):
    """Markdown'ni HTML'ga o'girish"""
    return markdown2.markdown(s, extras=["fenced-code-blocks", "tables", "break-on-newline"])


# ========== CONTEXT PROCESSORS ==========

@app.context_processor
def inject_globals():
    """Barcha template'larga global o'zgaruvchilar"""
    # Debug log (Render loglarida ko'rinadi)
    if not hasattr(app, '_log_shown'):
        print(f"DEBUG: FACEBOOK_PIXEL_ID={FACEBOOK_PIXEL_ID}")
        print(f"DEBUG: GA4_ID={GA4_ID}")
        app._log_shown = True
        
    return {
        'config': {
            'SITE_NAME': SITE_NAME,
            'SITE_DESCRIPTION': SITE_DESCRIPTION,
        },
        'GA4_ID': GA4_ID,
        'GOOGLE_ADS_ID': GOOGLE_ADS_ID,
        'FACEBOOK_PIXEL_ID': FACEBOOK_PIXEL_ID,
        'categories': CATEGORIES,
        'now': datetime.now()
    }


# ========== AUTH HELPERS ==========

def login_required(f):
    """Admin sahifalar uchun login tekshirish"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Iltimos, avval tizimga kiring.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== PUBLIC ROUTES ==========

@app.route('/')
def index():
    """Bosh sahifa — xizmatlar sahifasiga redirect"""
    return redirect(url_for('services'))


@app.route('/blog')
def blog():
    """Blog sahifasi — barcha postlar ro'yxati"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    query = Post.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=POSTS_PER_PAGE, error_out=False
    )
    
    # Eng ko'p o'qilgan postlar (Top 5)
    popular_posts = Post.query.filter_by(is_published=True).order_by(
        Post.views.desc()
    ).limit(5).all()
    
    return render_template('index.html', 
                          posts=pagination.items, 
                          pagination=pagination,
                          popular_posts=popular_posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    """ID orqali post sahifasi - slug ga redirect"""
    post = Post.query.get_or_404(post_id)
    if post.slug:
        return redirect(url_for('post_by_slug', slug=post.slug), code=301)
    
    # Agar slug yo'q bo'lsa, oddiy ko'rsatish
    post.views = (post.views or 0) + 1
    db.session.commit()
    
    related_posts = Post.query.filter(
        Post.id != post.id,
        Post.category == post.category,
        Post.is_published == True
    ).order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template('post.html', post=post, related_posts=related_posts)


@app.route('/blog/<slug>')
def post_by_slug(slug):
    """Slug orqali post sahifasi (SEO-friendly)"""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Ko'rishlar sonini oshirish
    post.views = (post.views or 0) + 1
    db.session.commit()
    
    # O'xshash postlarni olish (same category)
    related_posts = Post.query.filter(
        Post.id != post.id,
        Post.category == post.category,
        Post.is_published == True
    ).order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template('post.html', post=post, related_posts=related_posts)


@app.route('/search')
def search():
    """Qidiruv sahifasi"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if query:
        posts = Post.query.filter(
            Post.is_published == True,
            (Post.title.contains(query) | Post.content.contains(query) | Post.keywords.contains(query))
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    else:
        posts = None
    
    return render_template('search.html', posts=posts, query=query)


@app.route('/about')
def about():
    """Biz haqimizda sahifasi"""
    post_count = Post.query.filter_by(is_published=True).count()
    return render_template('about.html', post_count=post_count)


@app.route('/services')
def services():
    """Xizmatlar sahifasi"""
    return render_template('services.html', services=SERVICES_DATA)


@app.route('/services/<service_key>')
def service_detail(service_key):
    """Xizmat batafsil sahifasi (Ads Landing Page)"""
    service = SERVICES_DATA.get(service_key)
    if not service:
        abort(404)
    return render_template('service_detail.html', service=service, services=SERVICES_DATA)


@app.route('/portfolio')
def portfolio():
    """Portfolio sahifasi"""
    portfolios = Portfolio.query.filter_by(is_published=True).order_by(Portfolio.created_at.desc()).all()
    return render_template('portfolio.html', portfolios=portfolios)


@app.route('/portfolio/project/<slug>')
def portfolio_item(slug):
    """Loyiha batafsil sahifasi (Ads Landing Page)"""
    item = Portfolio.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # O'xshash loyihalar (same category)
    related_items = Portfolio.query.filter(
        Portfolio.id != item.id,
        Portfolio.category == item.category,
        Portfolio.is_published == True
    ).limit(3).all()
    
    return render_template('portfolio_detail.html', item=item, related_items=related_items)


@app.route('/order')
def order_page():
    """Alohida buyurtma sahifasi"""
    return render_template('order.html')


@app.route('/submit-order', methods=['POST'])
def submit_order():
    """Xizmatga yozilish formasi"""
    name = request.form.get('name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    budget = request.form.get('budget', '')
    message = request.form.get('message', '')
    
    # Service nomlarini o'zbekchaga o'girish
    service_names = {
        'ai_content': 'AI Kontent Generatsiya',
        'telegram_bot': 'Telegram Bot',
        'web_site': 'Web Sayt',
        'consulting': 'IT Konsalting',
        'smm': 'SMM Avtomatlashtirish',
        'ai_chatbot': 'AI Chatbot'
    }
    
    service_name = service_names.get(service, service)
    
    # Bazaga saqlash
    order = Order(
        name=name,
        phone=phone,
        service=service,
        service_name=service_name,
        budget=budget,
        message=message,
        status='new'
    )
    db.session.add(order)
    db.session.commit()
    
    # Telegram Admin ga yuborish
    try:
        from telegram_poster import send_to_admin
        
        budget_text = budget if budget else "Ko'rsatilmagan"
        message_text = message if message else "Yo'q"
        time_text = datetime.now().strftime('%d.%m.%Y %H:%M')
        
        order_message = f"""
🆕 *Yangi Buyurtma #{order.id}*

👤 *Ism:* {name}
📞 *Telefon:* {phone}
🛠️ *Xizmat:* {service_name}
💰 *Byudjet:* {budget_text}

💬 *Xabar:*
{message_text}

📅 *Vaqt:* {time_text}

🔗 Admin panel: /admin/orders
"""
        if send_to_admin(order_message):
            try:
                # Log to console/file
                print(f"✅ Order #{order.id} sent to Admin")
            except:
                pass
        else:
            print(f"❌ Failed to send Order #{order.id} to Admin")
    except Exception as e:
        print(f"Telegram yuborishda xato: {e}")
    
    flash(f'Rahmat, {name}! Arizangiz qabul qilindi. Tez orada siz bilan boglanamiz!', 'success')
    return redirect(url_for('services'))


# ========== ADMIN ROUTES ==========

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login sahifasi"""
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Tizimga muvaffaqiyatli kirdingiz!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login yoki parol noto\'g\'ri!', 'error')
    
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Chiqish"""
    session.clear()
    flash('Tizimdan chiqdingiz.', 'info')
    return redirect(url_for('index'))


@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Post statistikasi
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    
    # Buyurtmalar statistikasi
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    
    # Portfolio statistikasi
    total_portfolio = Portfolio.query.count()
    
    # So'nggi postlar
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # Eng ko'p ko'rilgan postlar
    top_posts = Post.query.filter_by(is_published=True).order_by(Post.views.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          total_posts=total_posts,
                          published_posts=published_posts,
                          total_views=total_views,
                          total_orders=total_orders,
                          new_orders=new_orders,
                          total_portfolio=total_portfolio,
                          recent_posts=recent_posts,
                          top_posts=top_posts)


@app.route('/admin/posts')
@login_required
def admin_posts():
    """Barcha postlarni boshqarish"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/posts.html', posts=posts)


@app.route('/admin/orders')
@login_required
def admin_orders():
    """Barcha buyurtmalarni ko'rish"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Statistika
    new_count = Order.query.filter_by(status='new').count()
    total_count = Order.query.count()
    
    return render_template('admin/orders.html', 
                          orders=orders, 
                          new_count=new_count,
                          total_count=total_count,
                          current_status=status_filter)


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    """Buyurtma statusini yangilash"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['new', 'contacted', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Buyurtma #{order.id} statusi yangilandi!', 'success')
    
    return redirect(url_for('admin_orders'))


@app.route('/admin/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def admin_delete_order(order_id):
    """Buyurtmani o'chirish"""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f'Buyurtma #{order_id} o\'chirildi!', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def admin_new_post():
    """Yangi post yaratish"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        topic = request.form.get('topic', 'Umumiy')
        category = request.form.get('category', 'Texnologiya')
        keywords = request.form.get('keywords', '')
        is_published = request.form.get('is_published') == 'on'
        
        post = Post(
            title=title,
            content=content,
            topic=topic,
            category=category,
            keywords=keywords,
            is_published=is_published
        )
        post.reading_time = post.calculate_reading_time()
        
        db.session.add(post)
        db.session.commit()
        
        post.slug = post.generate_slug()
        db.session.commit()
        
        flash('Post muvaffaqiyatli yaratildi!', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/edit_post.html', post=None, categories=CATEGORIES)


@app.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_post(post_id):
    """Postni tahrirlash"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.topic = request.form.get('topic')
        post.category = request.form.get('category')
        post.keywords = request.form.get('keywords')
        post.is_published = request.form.get('is_published') == 'on'
        post.reading_time = post.calculate_reading_time()
        
        db.session.commit()
        
        flash('Post muvaffaqiyatli yangilandi!', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/edit_post.html', post=post, categories=CATEGORIES)


@app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    """Postni o'chirish"""
    try:
        post = Post.query.get_or_404(post_id)
        post_title = post.title
        db.session.delete(post)
        db.session.commit()
        flash(f'"{post_title}" muvaffaqiyatli o\'chirildi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xatolik yuz berdi: {str(e)}', 'error')
        print(f"Post deletion error: {e}")
    
    return redirect(url_for('admin_posts'))


@app.route('/admin/generate', methods=['GET', 'POST'])
@login_required
def admin_generate():
    """AI bilan post generatsiya qilish (Asinxron)"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        category = request.form.get('category', 'Texnologiya')
        
        if not topic:
            flash('Mavzu kiritilishi shart!', 'error')
            return redirect(url_for('admin_generate'))
            
        from scheduler import generate_and_publish_post
        
        # Orqa fonda generatsiyani boshlash
        thread = threading.Thread(target=generate_and_publish_post, args=(topic, category))
        thread.daemon = True
        thread.start()
        
        flash(f'"{topic}" mavzusida generatsiya orqa fonda boshlandi. Tez orada Telegramga chiqadi.', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/generate.html', categories=CATEGORIES)


@app.route('/admin/migrate-slugs', methods=['POST'])
@login_required
def admin_migrate_slugs():
    """Barcha postlarga slug qo'shish (SEO uchun)"""
    posts_without_slug = Post.query.filter(
        (Post.slug == None) | (Post.slug == '')
    ).all()
    
    count = 0
    for post in posts_without_slug:
        post.slug = post.generate_slug()
        count += 1
    
    db.session.commit()
    flash(f'{count} ta postga slug qo\'shildi!', 'success')
    return redirect(url_for('admin_posts'))


# ========== PORTFOLIO ADMIN ROUTES ==========

@app.route('/admin/portfolio')
@login_required
def admin_portfolio():
    """Portfolio ro'yxati"""
    portfolios = Portfolio.query.order_by(Portfolio.created_at.desc()).all()
    return render_template('admin/portfolio.html', portfolios=portfolios)


@app.route('/admin/portfolio/new', methods=['GET', 'POST'])
@login_required
def admin_portfolio_new():
    """Yangi portfolio qo'shish"""
    if request.method == 'POST':
        portfolio = Portfolio(
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category', 'web'),
            emoji=request.form.get('emoji', '🚀'),
            technologies=request.form.get('technologies'),
            link=request.form.get('link'),
            image_url=request.form.get('image_url'),
            is_featured=request.form.get('is_featured') == 'on',
            is_published=request.form.get('is_published') == 'on',
            meta_description=request.form.get('meta_description'),
            meta_keywords=request.form.get('meta_keywords'),
            details=request.form.get('details'),
            features=request.form.get('features')
        )
        db.session.add(portfolio)
        db.session.commit()
        
        # Slug yaratish
        portfolio.slug = portfolio.generate_slug()
        db.session.commit()
        
        flash(f'"{portfolio.title}" muvaffaqiyatli qo\'shildi!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    return render_template('admin/portfolio_form.html', portfolio=None)


@app.route('/admin/portfolio/<int:portfolio_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_portfolio_edit(portfolio_id):
    """Portfolio tahrirlash"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    
    if request.method == 'POST':
        portfolio.title = request.form.get('title')
        portfolio.description = request.form.get('description')
        portfolio.category = request.form.get('category', 'web')
        portfolio.emoji = request.form.get('emoji', '🚀')
        portfolio.technologies = request.form.get('technologies')
        portfolio.link = request.form.get('link')
        portfolio.image_url = request.form.get('image_url')
        portfolio.is_featured = request.form.get('is_featured') == 'on'
        portfolio.is_published = request.form.get('is_published') == 'on'
        portfolio.meta_description = request.form.get('meta_description')
        portfolio.meta_keywords = request.form.get('meta_keywords')
        portfolio.details = request.form.get('details')
        portfolio.features = request.form.get('features')
        
        # Slug yangilash
        if not portfolio.slug:
            portfolio.slug = portfolio.generate_slug()
        
        db.session.commit()
        flash(f'"{portfolio.title}" yangilandi!', 'success')
        return redirect(url_for('admin_portfolio'))
    
    return render_template('admin/portfolio_form.html', portfolio=portfolio)


@app.route('/admin/portfolio/<int:portfolio_id>/delete', methods=['POST'])
@login_required
def admin_portfolio_delete(portfolio_id):
    """Portfolio o'chirish"""
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        title = portfolio.title
        db.session.delete(portfolio)
        db.session.commit()
        flash(f'"{title}" muvaffaqiyatli o\'chirildi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xatolik yuz berdi: {str(e)}', 'error')
        print(f"Portfolio deletion error: {e}")
        
    return redirect(url_for('admin_portfolio'))


@app.route('/admin/api/generate-portfolio')
@login_required
def api_generate_portfolio():
    """AI yordamida portfolio kontent generatsiya qilish"""
    from ai_generator import generate_portfolio_content
    
    title = request.args.get('title', '')
    category = request.args.get('category', 'web')
    
    if not title:
        return jsonify({'error': 'Title kerak'}), 400
    
    try:
        result = generate_portfolio_content(title, category)
        if result:
            return jsonify(result)
        return jsonify({'error': 'AI generatsiya muvaffaqiyatsiz'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== SEO ROUTES ==========

@app.route('/sitemap.xml')
def sitemap_xml():
    """Dinamik sitemap.xml generatsiyasi"""
    from flask import Response
    
    base_url = SITE_URL
    
    # Statik sahifalar
    pages = [
        {'loc': base_url, 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': f'{base_url}/about', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f'{base_url}/services', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f'{base_url}/portfolio', 'priority': '0.8', 'changefreq': 'weekly'},
    ]
    
    # Kategoriyalar
    for cat in CATEGORIES:
        pages.append({
            'loc': f'{base_url}/?category={cat}',
            'priority': '0.7',
            'changefreq': 'daily'
        })
    
    # Barcha postlar
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    for post in posts:
        if post.slug:
            url = f'{base_url}/blog/{post.slug}'
        else:
            url = f'{base_url}/post/{post.id}'
        
        lastmod = post.updated_at or post.created_at
        pages.append({
            'loc': url,
            'lastmod': lastmod.strftime('%Y-%m-%d') if lastmod else None,
            'priority': '0.6',
            'changefreq': 'weekly'
        })
    
    # XML generatsiya
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        if page.get('lastmod'):
            xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'
    
    xml += '</urlset>'
    
    return Response(xml, mimetype='application/xml')


@app.route('/api/catalog.xml')
def facebook_catalog():
    """Facebook Product Catalog Feed (RSS 2.0 formatda)"""
    from flask import Response
    
    base_url = SITE_URL
    portfolios = Portfolio.query.filter_by(is_published=True).all()
    
    # RSS 2.0 format - Facebook Commerce Manager uchun
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n'
    xml += '<channel>\n'
    xml += f'  <title>TrendoAI Portfolio - IT Xizmatlari</title>\n'
    xml += f'  <link>{base_url}/portfolio</link>\n'
    xml += f'  <description>TrendoAI professional IT xizmatlari va loyihalar katalogi</description>\n'
    
    for item in portfolios:
        # Kategoriya nomlari
        category_names = {
            'bot': 'Telegram Bot',
            'web': 'Web Sayt',
            'ai': 'AI Yechim',
            'mobile': 'Mobile App'
        }
        category_name = category_names.get(item.category, item.category)
        
        # Rasm URL
        image_url = item.image_url if item.image_url else f'{base_url}/static/favicon.svg'
        
        # Loyiha URL
        item_url = f'{base_url}/portfolio#{item.slug}' if item.slug else f'{base_url}/portfolio'
        
        xml += '  <item>\n'
        xml += f'    <g:id>{item.id}</g:id>\n'
        xml += f'    <title>{item.title}</title>\n'
        xml += f'    <link>{item_url}</link>\n'
        xml += f'    <description><![CDATA[{item.description}]]></description>\n'
        xml += f'    <g:image_link>{image_url}</g:image_link>\n'
        xml += f'    <g:brand>TrendoAI</g:brand>\n'
        xml += f'    <g:condition>new</g:condition>\n'
        xml += f'    <g:availability>in stock</g:availability>\n'
        xml += f'    <g:price>0 UZS</g:price>\n'  # Bepul konsultatsiya
        xml += f'    <g:product_type>{category_name}</g:product_type>\n'
        xml += f'    <g:google_product_category>Software > Computer Software > Business &amp; Productivity Software</g:google_product_category>\n'
        
        # SEO kalit so'zlar
        if item.meta_keywords:
            for keyword in item.meta_keywords.split(',')[:5]:
                xml += f'    <g:custom_label_0>{keyword.strip()}</g:custom_label_0>\n'
        
        xml += '  </item>\n'
    
    xml += '</channel>\n'
    xml += '</rss>'
    
    return Response(xml, mimetype='application/xml')


@app.route('/robots.txt')
def robots_txt():
    """robots.txt fayli"""
    from flask import Response
    
    content = f"""User-agent: *
Allow: /

# Sitemap joylashuvi
Sitemap: {SITE_URL}/sitemap.xml

# Admin va API sahifalarini yashirish
Disallow: /admin/
Disallow: /api/cron/

# Statik fayllarni ruxsat berish
Allow: /static/

# Crawl-delay (qidiruv botlari uchun)
Crawl-delay: 1

# TrendoAI - O'zbekiston texnologiya blog platformasi
"""
    return Response(content, mimetype='text/plain')


# ========== API ROUTES ==========

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'TrendoAI',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/posts')
def api_posts():
    """Barcha postlar API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', None)
    
    query = Post.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=min(per_page, 50), error_out=False
    )
    
    return jsonify({
        'posts': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@app.route('/api/posts/<int:post_id>')
def api_post(post_id):
    """Bitta post API"""
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@app.route('/api/stats')
def api_stats():
    """Statistika API"""
    return jsonify({
        'total_posts': Post.query.count(),
        'published_posts': Post.query.filter_by(is_published=True).count(),
        'total_views': db.session.query(db.func.sum(Post.views)).scalar() or 0,
        'categories': CATEGORIES
    })


# ========== CRON API ROUTES ==========

@app.route('/api/cron/generate-post', methods=['POST', 'GET'])
def cron_generate_post():
    """
    Tashqi Cron xizmatlari uchun post generatsiya endpoint (Asinxron).
    cron-job.org yoki boshqa xizmatlar orqali chaqiriladi.
    """
    import os
    
    # Secret key tekshirish
    cron_secret = os.getenv('CRON_SECRET', 'trendoai-cron-secret-2025')
    provided_secret = request.headers.get('X-Cron-Secret') or request.args.get('secret')
    
    if provided_secret != cron_secret:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from scheduler import generate_and_publish_post
    
    # Orqa fonda generatsiyani boshlash
    thread = threading.Thread(target=generate_and_publish_post)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'message': 'Post generatsiyasi orqa fonda boshlandi (Asinxron)',
        'timestamp': datetime.now().isoformat()
    }), 202


@app.route('/api/init-db')
def init_database():
    """
    Database jadvallarini yaratish va tekshirish.
    Order jadvali yo'q bo'lsa yaratadi.
    """
    try:
        # Barcha jadvallarni yaratish
        db.create_all()
        
        # Order jadvalini tekshirish
        order_count = Order.query.count()
        post_count = Post.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Database jadvallar muvaffaqiyatli yaratildi/yangilandi',
            'tables': {
                'orders': order_count,
                'posts': post_count
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/cron/status')
def cron_status():
    """Cron vazifalar statusi"""
    try:
        from scheduler import get_scheduled_jobs
        jobs = get_scheduled_jobs()
        return jsonify({
            'status': 'ok',
            'scheduled_jobs': len(jobs),
            'jobs': jobs,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ========== SEO ROUTES ==========

@app.route('/sitemap.xml')
def sitemap():
    """Dynamic sitemap"""
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Static pages
    for route in ['index', 'about', 'services']:
        xml += f'  <url><loc>https://trendoai.uz/{route if route != "index" else ""}</loc></url>\n'
    
    # Posts
    for post in posts:
        xml += f'  <url><loc>https://trendoai.uz/post/{post.id}</loc></url>\n'
    
    xml += '</urlset>'
    
    return xml, 200, {'Content-Type': 'application/xml'}


@app.route('/robots.txt')
def robots():
    """Robots.txt"""
    txt = """User-agent: *
Allow: /
Sitemap: https://trendoai.uz/sitemap.xml
"""
    return txt, 200, {'Content-Type': 'text/plain'}


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(e):
    """404 sahifa"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """500 sahifa"""
    print(f"Server Error (500): {e}")
    import traceback
    traceback.print_exc()
    return render_template('errors/500.html'), 500


# ========== STARTUP ==========

# ========== STARTUP ==========

# Server ishga tushganda bajariladigan amallar (Gunicorn va Local)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database error: {e}")

# Database Migration - Add missing columns at startup
def migrate_portfolio_columns():
    """Add missing columns to Portfolio table if they don't exist"""
    try:
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('portfolio')]
        
        with db.engine.connect() as conn:
            if 'details' not in columns:
                conn.execute(text("ALTER TABLE portfolio ADD COLUMN details TEXT"))
                print("✅ Added 'details' column to Portfolio")
            if 'features' not in columns:
                conn.execute(text("ALTER TABLE portfolio ADD COLUMN features TEXT"))
                print("✅ Added 'features' column to Portfolio")
            conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

# Run migration
with app.app_context():
    migrate_portfolio_columns()

# Auto-generate slugs for portfolio items without slugs
def generate_portfolio_slugs():
    """Generate slugs for portfolio items that don't have one"""
    import re
    try:
        portfolios = Portfolio.query.filter(
            (Portfolio.slug == None) | (Portfolio.slug == '')
        ).all()
        
        if not portfolios:
            return
        
        for item in portfolios:
            if item.title:
                # Simple slug generation
                slug = item.title.lower()
                slug = re.sub(r'[^a-z0-9\s-]', '', slug)
                slug = re.sub(r'[\s_]+', '-', slug)
                slug = slug.strip('-')
                
                if slug:
                    # Ensure unique
                    base_slug = slug
                    counter = 1
                    while Portfolio.query.filter_by(slug=slug).first():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    item.slug = slug
                    print(f"✅ Generated slug: {item.title} -> {slug}")
        
        db.session.commit()
        print("✅ Portfolio slugs generated successfully")
    except Exception as e:
        print(f"Slug generation note: {e}")

# Run slug generation
with app.app_context():
    generate_portfolio_slugs()

# Avtomatlashtirish va Botni ishga tushirish
try:
    from scheduler import scheduler
    from bot_service import setup_webhook
    
    # Scheduler ishga tushirish
    scheduler.start()
    
    
    # Webhook rejimida bot (polling o'rniga)
    # Threading ichida ishlaydi, shuning uchun main thread bloklanmaydi
    setup_webhook(app)
    
    print("🚀 TrendoAI xizmatlari (Scheduler + Webhook Bot) ishga tushdi!")
except Exception as e:
    print(f"Service startup error: {e}")


if __name__ == '__main__':
    # Flask ilovasini ishga tushirish
    app.run(debug=True, use_reloader=False, port=5000)