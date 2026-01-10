from app.extensions import db

# Many-to-Many for Paper Authors
paper_authors = db.Table('paper_authors',
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'), primary_key=True),
    db.Column('researcher_id', db.Integer, db.ForeignKey('researchers.id'), primary_key=True)
)

class Researcher(db.Model):
    __tablename__ = 'researchers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    affiliation = db.Column(db.String(200), nullable=True)
    h_index = db.Column(db.Integer, nullable=True)
    scholar_profile_url = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'affiliation': self.affiliation,
            'h_index': self.h_index
        }

class Paper(db.Model):
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    external_links = db.Column(db.JSON, nullable=True) # e.g. {"doi": "...", "scholar": "..."}
    is_featured = db.Column(db.Boolean, default=False)
    
    # Check if linked to specific edition or generic conference? Prompt said "conference_id".
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)
    
    authors = db.relationship('Researcher', secondary=paper_authors, backref=db.backref('papers', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.publication_year,
            'featured': self.is_featured,
            'authors': [a.name for a in self.authors],
            'links': self.external_links
        }

class Workshop(db.Model):
    __tablename__ = 'workshops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organizer = db.Column(db.String(150), nullable=True)
    trainer = db.Column(db.String(150), nullable=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organizer': self.organizer,
            'trainer': self.trainer
        }
