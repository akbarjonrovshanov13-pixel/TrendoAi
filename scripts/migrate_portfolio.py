import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        print("Migrating Portfolio table...")
        try:
            # Check if columns exist and add if not
            with db.engine.connect() as conn:
                # detail column
                try:
                    conn.execute(text("ALTER TABLE portfolio ADD COLUMN details TEXT"))
                    print("Added 'details' column.")
                except Exception as e:
                    print(f"'details' column might already exist: {e}")
                
                # features column
                try:
                    conn.execute(text("ALTER TABLE portfolio ADD COLUMN features TEXT"))
                    print("Added 'features' column.")
                except Exception as e:
                    print(f"'features' column might already exist: {e}")
                
                conn.commit()
            print("Migration completed successfully.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
