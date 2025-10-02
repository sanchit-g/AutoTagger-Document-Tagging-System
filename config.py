"""
Configuration settings for AutoTagger application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Flask Configuration
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/autotagger.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Settings
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf'}
    
    # NLP Settings
    NLP_MODEL = 'en_core_web_sm'
    MAX_KEYWORDS = 10
    MIN_KEYWORD_LENGTH = 3
    SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score to consider documents related
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'logs' / 'autotagger.log'
    
    # API Settings
    RESULTS_PER_PAGE = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}