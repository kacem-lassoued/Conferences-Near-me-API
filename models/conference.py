from db import db

# Many-to-Many relationship between Conference and Theme
conference_themes = db.Table('conference_themes',
    db.Column('conference_id', db.Integer, db.ForeignKey('conferences.id'), primary_key=True),
    db.Column('theme_id', db.Integer, db.ForeignKey('themes.id'), primary_key=True)
)

class Theme(db.Model):
    __tablename__ = 'themes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    parent_theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    
    # Self-referential relationship for hierarchy
    children = db.relationship('Theme', backref=db.backref('parent', remote_side=[id]))

class Conference(db.Model):
    __tablename__ = 'conferences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    acronym = db.Column(db.String(20), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    country = db.Column(db.String(100), nullable=True, index=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    status = db.Column(db.String(50), default='scheduled') # scheduled, cancelled, postponed
    source = db.Column(db.String(50), default='manual')
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    
    # Submission fields
    organizers = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(500), nullable=True)  # Google Maps format
    featured_papers = db.Column(db.JSON, nullable=True)  # Array of paper titles
    featured_workshops = db.Column(db.Text, nullable=True)
    
    # Classification fields
    classification = db.Column(db.JSON, nullable=True)  # {primary: str, secondary: [str], confidence: float}

    # Relationships
    themes = db.relationship('Theme', secondary=conference_themes, backref=db.backref('conferences', lazy='dynamic'))
    editions = db.relationship('ConferenceEdition', backref='conference', lazy=True, cascade='all, delete-orphan')
    rankings = db.relationship('Ranking', backref='conference', lazy=True, cascade='all, delete-orphan')

class ConferenceEdition(db.Model):
    __tablename__ = 'conference_editions'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    venue = db.Column(db.String(200), nullable=True)
    acceptance_rate = db.Column(db.Float, nullable=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)

class Ranking(db.Model):
    __tablename__ = 'rankings'

    id = db.Column(db.Integer, primary_key=True)
    ranking_name = db.Column(db.String(50), nullable=False) # CORE, SCImago
    rank = db.Column(db.String(20), nullable=True) # A*, A, B
    score = db.Column(db.Float, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)
