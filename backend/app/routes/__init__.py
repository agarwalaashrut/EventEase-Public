"""Blueprint initialization."""
from flask import Blueprint, jsonify

# Health check blueprint
health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


# Import blueprints
from .events import events_bp
from .users import users_bp
from .invitations import invitations_bp
from .voting import voting_bp
