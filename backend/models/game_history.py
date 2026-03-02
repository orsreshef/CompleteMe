"""
GameHistory model — SQLAlchemy ORM definition for the game_history table.
"""

from datetime import datetime, timezone
from extensions import db


class GameHistory(db.Model):
    __tablename__ = 'game_history'

    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)
    num_missing_pieces = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    score_earned = db.Column(db.Integer, default=0)
    played_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'difficulty_level': self.difficulty_level,
            'grid_size': self.grid_size,
            'num_missing_pieces': self.num_missing_pieces,
            'success': self.success,
            'score_earned': self.score_earned,
            'played_at': self.played_at.isoformat() if self.played_at else None,
        }
