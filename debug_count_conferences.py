
from app import app
from db import db
from models import Conference

def check_count():
    with app.app_context():
        count = Conference.query.count()
        print(f"Current conference count: {count}")
        if count > 0:
            first = Conference.query.first()
            print(f"Sample: {first.name} ({first.source})")

if __name__ == "__main__":
    check_count()
