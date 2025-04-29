"""
Inicjalizacja aplikacji Flask.
"""
import os
from flask import Flask

def create_app():
    """
    Utworzenie instancji aplikacji Flask.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')

    os.makedirs('db', exist_ok=True)

    # Inicjalizacja ścieżek
    from .routes import init_app
    init_app(app)

    return app
