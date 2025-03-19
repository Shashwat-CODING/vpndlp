from app import db
from datetime import datetime

class Playlist(db.Model):
    """Model for storing playlists"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlaylistItem(db.Model):
    """Model for storing playlist items (YouTube videos)"""
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id', ondelete='CASCADE'), nullable=False)
    youtube_url = db.Column(db.String(512), nullable=False)
    title = db.Column(db.String(256))
    duration = db.Column(db.Integer)  # Duration in seconds
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship with Playlist
    playlist = db.relationship('Playlist', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))

class AudioCache(db.Model):
    """Model for tracking cached audio files"""
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(512), unique=True, nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    size_bytes = db.Column(db.Integer)
