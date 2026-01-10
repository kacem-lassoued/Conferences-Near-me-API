from app import app
from db import db
from models import Paper, Author, Conference

def count_stats():
    with app.app_context():
        paper_count = Paper.query.count()
        author_count = Author.query.count()
        conf_count = Conference.query.count()
        
        print(f"Stats:")
        print(f"- Conferences: {conf_count}")
        print(f"- Papers: {paper_count}")
        print(f"- Authors: {author_count}")
        
        # Show a sample paper
        if paper_count > 0:
            p = Paper.query.first()
            print(f"\nSample Paper: {p.title}")
            print(f"Authors: {[a.name for a in p.authors]}")

if __name__ == "__main__":
    count_stats()
