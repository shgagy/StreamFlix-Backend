from src.models.user import db
from datetime import datetime

# Association table for many-to-many relationship between content and genres
content_genres = db.Table('content_genres',
    db.Column('content_id', db.Integer, db.ForeignKey('content.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Genre {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(20), nullable=False)  # 'movie' or 'series'
    cover_image = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))
    release_year = db.Column(db.Integer)
    duration = db.Column(db.Integer)  # in minutes for movies
    rating = db.Column(db.Float, default=0.0)
    imdb_rating = db.Column(db.Float)
    language = db.Column(db.String(50))
    country = db.Column(db.String(100))
    director = db.Column(db.String(200))
    cast = db.Column(db.Text)  # JSON string of cast members
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For movies only
    video_url = db.Column(db.String(500))  # Direct video URL for movies
    
    # Relationships
    genres = db.relationship('Genre', secondary=content_genres, lazy='subquery',
                           backref=db.backref('content', lazy=True))
    episodes = db.relationship('Episode', backref='series', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='content', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='content', lazy=True, cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='content', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='content', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Content {self.title} ({self.content_type})>'

    def calculate_average_rating(self):
        if self.ratings:
            total = sum(rating.score for rating in self.ratings)
            self.rating = total / len(self.ratings)
        else:
            self.rating = 0.0
        db.session.commit()

    def to_dict(self, include_episodes=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'cover_image': self.cover_image,
            'trailer_url': self.trailer_url,
            'release_year': self.release_year,
            'duration': self.duration,
            'rating': self.rating,
            'imdb_rating': self.imdb_rating,
            'language': self.language,
            'country': self.country,
            'director': self.director,
            'cast': self.cast,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'video_url': self.video_url,
            'genres': [genre.to_dict() for genre in self.genres]
        }
        
        if include_episodes and self.content_type == 'series':
            data['episodes'] = [episode.to_dict() for episode in self.episodes]
            
        return data

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    episode_number = db.Column(db.Integer, nullable=False)
    season_number = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    video_url = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    air_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Episode S{self.season_number}E{self.episode_number}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'series_id': self.series_id,
            'title': self.title,
            'description': self.description,
            'episode_number': self.episode_number,
            'season_number': self.season_number,
            'duration': self.duration,
            'video_url': self.video_url,
            'thumbnail': self.thumbnail,
            'air_date': self.air_date.isoformat() if self.air_date else None,
            'is_active': self.is_active,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

