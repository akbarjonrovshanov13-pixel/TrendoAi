
import sys
import os
import json

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Service, SERVICES_DATA

def migrate_services():
    """Migrate services from dictionary to database"""
    with app.app_context():
        # Create table if not exists
        db.create_all()
        
        print("Migrating services...")
        count = 0
        
        for key, data in SERVICES_DATA.items():
            # Check if service already exists
            existing = Service.query.filter_by(slug=key).first()
            if existing:
                print(f"Skipping {key} (already exists)")
                continue
                
            # Create new service
            service = Service(
                slug=key,
                title=data['title'],
                description=data.get('description', ''),
                full_description=data.get('full_description', ''),
                price=data.get('price', ''),
                icon=data.get('icon', ''),
                features=json.dumps(data.get('features', [])),
                meta_desc=data.get('meta_desc', ''),
                image_url=f"/static/images/services/{key}.jpg", # Default path
                is_active=True,
                order=count
            )
            
            # Handle discount
            if 'discount' in data:
                service.discount_percent = data['discount'].get('percent', 0)
                service.discount_until = data['discount'].get('until', '')
            
            db.session.add(service)
            print(f"Added: {data['title']}")
            count += 1
            
        db.session.commit()
        print(f"Migration complete! Added {count} services.")

if __name__ == "__main__":
    migrate_services()
