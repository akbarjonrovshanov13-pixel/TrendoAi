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
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklash
load_dotenv()

app = Flask(__name__)

# Konfiguratsiya
from config import (
    SITE_URL, SITE_NAME, SITE_DESCRIPTION, DATABASE_URI, SECRET_KEY,
    ADMIN_USERNAME, ADMIN_PASSWORD, POSTS_PER_PAGE, CATEGORIES
)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)


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


# ========== TEMPLATE FILTERS ==========

@app.template_filter('markdown')
def markdown_filter(s):
    """Markdown'ni HTML'ga o'girish"""
    return markdown2.markdown(s, extras=["fenced-code-blocks", "tables", "break-on-newline"])


# ========== CONTEXT PROCESSORS ==========

@app.context_processor
def inject_globals():
    """Barcha template'larga global o'zgaruvchilar"""
    return {
        'config': {
            'SITE_NAME': SITE_NAME,
            'SITE_DESCRIPTION': SITE_DESCRIPTION,
        },
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
    """Bosh sahifa — barcha postlar ro'yxati"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    query = Post.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=POSTS_PER_PAGE, error_out=False
    )
    
    return render_template('index.html', 
                          posts=pagination.items, 
                          pagination=pagination)


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
    return render_template('services.html')


@app.route('/portfolio')
def portfolio():
    """Portfolio sahifasi"""
    return render_template('portfolio.html')


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
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(Post.views)).scalar() or 0
    
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                          total_posts=total_posts,
                          published_posts=published_posts,
                          total_views=total_views,
                          recent_posts=recent_posts)


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
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Post o\'chirildi!', 'success')
    return redirect(url_for('admin_posts'))


@app.route('/admin/generate', methods=['GET', 'POST'])
@login_required
def admin_generate():
    """AI bilan post generatsiya qilish"""
    if request.method == 'POST':
        topic = request.form.get('topic')
        category = request.form.get('category', 'Texnologiya')
        
        from ai_generator import generate_post_for_seo
        from image_fetcher import get_image_for_topic
        
        post_data = generate_post_for_seo(topic)
        
        if post_data:
            # Rasm olish
            image_url = get_image_for_topic(topic)
            
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                topic=topic,
                category=category,
                keywords=post_data['keywords'],
                image_url=image_url,
                is_published=True
            )
            post.reading_time = post.calculate_reading_time()
            
            db.session.add(post)
            db.session.commit()
            
            post.slug = post.generate_slug()
            db.session.commit()
            
            # Telegram kanalga yuborish
            try:
                from telegram_poster import send_to_telegram_channel, send_photo_to_channel
                from config import SITE_URL
                
                post_url = f"{SITE_URL}/post/{post.id}"
                tg_caption = f"""📝 *Yangi Maqola!*

*{post.title}*

🏷 Kategoriya: #{category.replace(' ', '_')}
⏱ O'qish vaqti: {post.reading_time} daqiqa

🔗 [Maqolani o'qish]({post_url})

#TrendoAI #Texnologiya"""

                # Rasm bilan yuborish
                if image_url:
                    send_photo_to_channel(image_url, tg_caption)
                else:
                    send_to_telegram_channel(tg_caption)
                    
                flash(f'"{post.title}" muvaffaqiyatli generatsiya qilindi va Telegramga yuborildi!', 'success')
            except Exception as e:
                print(f"Telegram xatosi: {e}")
                flash(f'"{post.title}" muvaffaqiyatli generatsiya qilindi!', 'success')
            
            return redirect(url_for('admin_posts'))
        else:
            flash('Generatsiya qilishda xatolik yuz berdi!', 'error')
    
    return render_template('admin/generate.html', categories=CATEGORIES)


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


@app.route('/robots.txt')
def robots_txt():
    """robots.txt fayli"""
    from flask import Response
    
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml

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
    Tashqi Cron xizmatlari uchun post generatsiya endpoint.
    cron-job.org yoki boshqa xizmatlar orqali chaqiriladi.
    """
    import os
    import random
    
    # Secret key tekshirish (xavfsizlik uchun)
    cron_secret = os.getenv('CRON_SECRET', 'trendoai-cron-secret-2025')
    
    # Header yoki query param orqali secret tekshirish
    provided_secret = request.headers.get('X-Cron-Secret') or request.args.get('secret')
    
    if provided_secret != cron_secret:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid or missing CRON_SECRET'
        }), 401
    
    try:
        from scheduler import TOPICS, generate_and_publish_post
        
        # Generatsiya qilish
        generate_and_publish_post()
        
        return jsonify({
            'status': 'success',
            'message': 'Post muvaffaqiyatli generatsiya qilindi!',
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
    return render_template('errors/500.html'), 500


# ========== STARTUP ==========

# ========== STARTUP ==========

# Server ishga tushganda bajariladigan amallar (Gunicorn va Local)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database error: {e}")

# Avtomatlashtirish va Botni ishga tushirish
try:
    from scheduler import scheduler
    from bot_service import setup_webhook
    
    # Scheduler ishga tushirish
    scheduler.start()
    
    # Webhook rejimida bot (polling o'rniga)
    setup_webhook(app)
    
    print("🚀 TrendoAI xizmatlari (Scheduler + Webhook Bot) ishga tushdi!")
except Exception as e:
    print(f"Service startup error: {e}")


if __name__ == '__main__':
    # Flask ilovasini ishga tushirish
    app.run(debug=True, use_reloader=False, port=5000)