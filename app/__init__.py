# server/app/__init__.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask
from flask_cors import CORS
from app.routes.game_routes import game_routes
from app.routes.card_routes import card_routes

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for development
    
    # Register blueprints
    app.register_blueprint(game_routes, url_prefix='/api')
    app.register_blueprint(card_routes, url_prefix='/api')
    return app
