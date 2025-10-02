"""
AutoTagger Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
from pathlib import Path

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Create necessary directories
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['LOG_FILE']).parent.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    setup_logging(app)
    
    # Register error handlers
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    app.logger.info('AutoTagger application started')
    
    return app

def setup_logging(app):
    """Configure application logging"""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    
    # File handler
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)