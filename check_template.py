
from app import app, db, Portfolio
from flask import render_template

with app.app_context():
    try:
        portfolios = Portfolio.query.order_by(Portfolio.created_at.desc()).all()
        # We need a request context to render template because of url_for used in templates
        with app.test_request_context():
            output = render_template('admin/portfolio.html', portfolios=portfolios)
            print("Template rendered successfully!")
            # print(output[:500])
    except Exception as e:
        import traceback
        traceback.print_exc()
