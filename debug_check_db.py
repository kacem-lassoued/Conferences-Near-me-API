from app import app
from models import Conference

def check():
    with app.app_context():
        # Check Barcelona
        confs = Conference.query.filter(Conference.city.like('%Barcelona%')).all()
        print(f"Barcelona Conferences: {len(confs)}")
        for c in confs:
            print(f"  {c.name}: {c.latitude}, {c.longitude}")

        # Check total with coords
        count = Conference.query.filter(Conference.latitude.isnot(None)).count()
        print(f"Total conferences with coords: {count}")

if __name__ == "__main__":
    check()
