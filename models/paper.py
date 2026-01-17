from db import db

class Paper(db.Model):
    """
    Represents an academic paper submitted with a conference.
    Papers can have multiple authors (many-to-many relationship).
    """
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)
    
    # Relationship to conference
    conference = db.relationship('Conference', backref=db.backref('papers', lazy=True, cascade='all, delete-orphan'))
    
    # Relationship to authors (many-to-many)
    # Import the association table from author.py
    from models.author import paper_authors
    authors = db.relationship('Author', secondary=paper_authors, back_populates='papers')
    
    def __repr__(self):
        return f'<Paper "{self.title}">'
