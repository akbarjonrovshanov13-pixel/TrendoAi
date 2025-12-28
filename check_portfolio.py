
from app import app, db, Portfolio

with app.app_context():
    try:
        portfolios = Portfolio.query.all()
        print(f"Successfully fetched {len(portfolios)} portfolios.")
        for p in portfolios:
            print(f"- {p.title} (ID: {p.id})")
    except Exception as e:
        print(f"Error fetching portfolios: {e}")
