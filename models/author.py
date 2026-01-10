from db import db
from datetime import datetime

# Many-to-Many relationship between Paper and Author
paper_authors = db.Table('paper_authors',
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True)
)

class Author(db.Model):
    """
    Represents an author of academic papers.
    Stores h-index fetched from Semantic Scholar API.
    """
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    h_index = db.Column(db.Integer, nullable=True)  # H-index from Semantic Scholar
    semantic_scholar_id = db.Column(db.String(100), nullable=True, unique=True)  # External ID for caching
    affiliation = db.Column(db.String(300), nullable=True)  # Author's institution
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)  # Last time h-index was fetched
    
    # Relationship to papers
    papers = db.relationship('Paper', secondary=paper_authors, back_populates='authors')
    
    def __repr__(self):
        return f'<Author {self.name} (h-index: {self.h_index})>'
