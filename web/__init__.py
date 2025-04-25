from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    
    # Ensure the database directory exists
    os.makedirs('db', exist_ok=True)
    
    # Register routes
    from .routes import init_app
    init_app(app)
    
    return app