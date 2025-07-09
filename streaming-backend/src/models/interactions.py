from src.models.user import db
from datetime import datetime

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 1-10 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate ratings
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content_rating'),)

    def __repr__(self):
        return f'<Rating {self.score} by User {self.user_id} for Content {self.content_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'username': self.user.username if self.user else None
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # For replies
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __repr__(self):
        return f'<Comment by User {self.user_id} for Content {self.content_id}>'

    def to_dict(self, include_replies=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'text': self.text,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'username': self.user.username if self.user else None
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies if reply.is_active]
            
        return data

class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'))  # For series episodes
    watch_time = db.Column(db.Integer, default=0)  # Time watched in seconds
    total_time = db.Column(db.Integer)  # Total duration in seconds
    completed = db.Column(db.Boolean, default=False)
    last_watched = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint for user-content-episode combination
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', 'episode_id', name='unique_watch_history'),)

    def __repr__(self):
        return f'<WatchHistory User {self.user_id} Content {self.content_id}>'

    @property
    def progress_percentage(self):
        if self.total_time and self.total_time > 0:
            return min(100, (self.watch_time / self.total_time) * 100)
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'episode_id': self.episode_id,
            'watch_time': self.watch_time,
            'total_time': self.total_time,
            'completed': self.completed,
            'progress_percentage': self.progress_percentage,
            'last_watched': self.last_watched.isoformat() if self.last_watched else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'content': self.content.to_dict() if self.content else None
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate favorites
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content_favorite'),)

    def __repr__(self):
        return f'<Favorite User {self.user_id} Content {self.content_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'content': self.content.to_dict() if self.content else None
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'new_episode', 'new_season', 'recommendation'
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='notifications')
    content = db.relationship('Content', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title} for User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'content_id': self.content_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'content': self.content.to_dict() if self.content else None
        }

