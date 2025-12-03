"""Flask application factory."""
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from pymongo import MongoClient

socketio = SocketIO()
mongo_client = None


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name:
        app.config.from_object(f'app.config.{config_name}')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Initialize MongoDB
    global mongo_client
    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = mongo_client[app.config['DB_NAME']]
    
    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize Socket.IO
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        async_mode='eventlet'
    )
     # Initialize Email service
    from app.services.email_service import init_mail
    init_mail(app)
    
    # Register blueprints
    from app.routes import events_bp, health_bp, users_bp, invitations_bp, voting_bp, auth_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(invitations_bp, url_prefix='/api/invitations')
    app.register_blueprint(voting_bp)
    app.register_blueprint(auth_bp)
    
    return app


def close_db():
    """Close database connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()
