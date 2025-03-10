# app.py - Main Application
# Main entry point that sets up the Flask application

import os
from flask import Flask
from dotenv import load_dotenv

# Import components
from config import Config
from database import init_db
from webhook_handler import webhook_bp
from health_check import health_bp
from message_handler import message_bp

# Load environment variables
load_dotenv()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(webhook_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(message_bp)
    
    # Initialize database at startup
    with app.app_context():
        init_db()
    
    @app.route('/')
    def index():
        return "TTD Survey Bot is running. Webhook endpoint: /webhook"
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)