"""User model — SQLAlchemy ORM definition for the users table."""

from datetime import datetime, timezone
from extensions import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_id = db.Column(db.Integer, default=1)
    total_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    game_history = db.relationship('GameHistory', backref='user', lazy=True)

    def set_password(self, plain_password):
        """Hash and store the password."""
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password):
        """Check a plain password against the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    def to_dict(self):
        """Return a safe public representation (no password hash)."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'avatar_id': self.avatar_id,
            'total_score': self.total_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
