# backend/app/seed_data/seed_hierarchy.py
import json
from pathlib import Path
from sqlalchemy.orm import Session
from .. import models, database

JSON_PATH = Path(__file__).with_name("doc_hierarchy.json")

def run_seed():
    data = json.loads(JSON_PATH.read_text())
    db: Session = database.SessionLocal()
    try:
        for dept in data:
            for cat in dept["categories"]:
                for sub in cat["subcategories"]:
                    # Check if the record already exists
                    exists = db.query(models.DocHierarchy).filter_by(
                        department=dept["department"],
                        category=cat["category"],
                        subcategory=sub
                    ).first()

                    if not exists:
                        db.add(models.DocHierarchy(
                            department=dept["department"],
                            category=cat["category"],
                            subcategory=sub
                        ))

        db.commit()
        print("Doc hierarchy seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()
