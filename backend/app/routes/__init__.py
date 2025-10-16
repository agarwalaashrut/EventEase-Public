"""Blueprint initialization."""
from flask import Blueprint, jsonify

# Health check blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


# Auth blueprint (placeholder)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint placeholder."""
    return jsonify({'message': 'Auth endpoint placeholder'}), 501


# Import events blueprint from events.py
from .events import events_bp
