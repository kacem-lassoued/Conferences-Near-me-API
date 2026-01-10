from app.extensions import db

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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_theme_id
        }

class Conference(db.Model):
    __tablename__ = 'conferences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    acronym = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    status = db.Column(db.String(50), default='scheduled') # scheduled, cancelled, postponed
    source = db.Column(db.String(50), default='manual')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships:
    # these allow us to easily access related data (e.g. conference.papers)
    # without writing complex SQL queries manually.
    themes = db.relationship('Theme', secondary=conference_themes, backref=db.backref('conferences', lazy='dynamic'))
    editions = db.relationship('ConferenceEdition', backref='conference', lazy=True, cascade='all, delete-orphan')
    rankings = db.relationship('Ranking', backref='conference', lazy=True, cascade='all, delete-orphan')
    papers = db.relationship('Paper', backref='conference', lazy=True, cascade='all, delete-orphan')
    workshops = db.relationship('Workshop', backref='conference', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
            'website': self.website,
            'dates': {
                'start': str(self.start_date) if self.start_date else None,
                'end': str(self.end_date) if self.end_date else None
            },
            'location': {
                'country': self.country,
                'city': self.city,
                'coordinates': {
                    'lat': self.latitude,
                    'lng': self.longitude
                }
            },
            'status': self.status,
            'themes': [t.name for t in self.themes],
            'rankings': [r.to_dict() for r in self.rankings]
        }

class ConferenceEdition(db.Model):
    __tablename__ = 'conference_editions'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    venue = db.Column(db.String(200), nullable=True)
    acceptance_rate = db.Column(db.Float, nullable=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'venue': self.venue,
            'acceptance_rate': self.acceptance_rate
        }

class Ranking(db.Model):
    __tablename__ = 'rankings'

    id = db.Column(db.Integer, primary_key=True)
    ranking_name = db.Column(db.String(50), nullable=False) # CORE, SCImago
    rank = db.Column(db.String(20), nullable=True) # A*, A, B
    score = db.Column(db.Float, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)

    def to_dict(self):
        return {
            'system': self.ranking_name,
            'rank': self.rank,
            'score': self.score,
            'year': self.year
        }
