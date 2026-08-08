"""Application configuration — loaded via get_config() in app.py."""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')
    UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY', '')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'static', 'temp')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    DIFFICULTY_LEVELS = {
        1: {'pieces': 2, 'name': 'Beginner'},
        2: {'pieces': 4, 'name': 'Easy'},
        3: {'pieces': 8, 'name': 'Medium'},
        4: {'pieces': 16, 'name': 'Hard'},
        5: {'pieces': 32, 'name': 'Expert'}
    }

    VALIDATION_THRESHOLD = 0.75  # 75% similarity required for a match
    USE_ENSEMBLE_VALIDATION = False
    FAST_MODE = False

    UNSPLASH_API_URL = 'https://api.unsplash.com'
    UNSPLASH_RANDOM_ENDPOINT = '/photos/random'
    UNSPLASH_PER_PAGE = 30

    MAX_IMAGE_DIMENSION = 1200
    PUZZLE_PIECE_SIZE = 150
    DECOY_COUNT = 5  # Pool always has 6 pieces: correct + (6 - num_regions) decoys

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://puzzle_user:puzzle_password@localhost/puzzle_game_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_SECURE = False       # Set True in production (HTTPS only)
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_CSRF_PROTECT = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Return the configuration class for the given environment name."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
