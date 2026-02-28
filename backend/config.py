"""
Configuration Module
Contains all configuration settings for the application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.getenv(
        'SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    # API Keys
    UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')
    UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY', '')

    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'static', 'temp')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Puzzle settings
    DIFFICULTY_LEVELS = {
        1: {'pieces': 2, 'name': 'Beginner'},
        2: {'pieces': 4, 'name': 'Easy'},
        3: {'pieces': 8, 'name': 'Medium'},
        4: {'pieces': 16, 'name': 'Hard'},
        5: {'pieces': 32, 'name': 'Expert'}
    }

    # Validation settings
    VALIDATION_THRESHOLD = 0.75  # 75% similarity required for match
    # Set to True for more accurate but slower validation
    USE_ENSEMBLE_VALIDATION = False
    FAST_MODE = False  # Set to True for faster validation with slightly lower accuracy

    # Unsplash API settings
    UNSPLASH_API_URL = 'https://api.unsplash.com'
    UNSPLASH_RANDOM_ENDPOINT = '/photos/random'
    UNSPLASH_PER_PAGE = 30

    # Image processing settings
    MAX_IMAGE_DIMENSION = 1200  # Max width/height for uploaded images
    PUZZLE_PIECE_SIZE = 150  # Default size for puzzle pieces in pixels
    DECOY_COUNT = 5  # Default decoys; actual count = 6 - num_regions (pool always has 6 pieces)

    # CORS settings
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', 'http://localhost:3000').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # In production, make sure to set proper SECRET_KEY and API keys


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration based on environment

    Args:
        env: environment name ('development', 'production', 'testing')

    Returns:
        Config class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    return config.get(env, config['default'])
