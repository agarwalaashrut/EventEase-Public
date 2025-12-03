"""
Users API routes
Handles user authentication and registration
"""
from flask import Blueprint, jsonify, request, current_app
from app.models.user import User
from datetime import datetime
import hashlib

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def hash_password(password: str) -> str:
    """Simple password hashing using SHA-256 (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_db():
    """Get database connection from current app"""
    return current_app.db


@users_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    POST /api/users/register
    Body: {email, name, password}
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = User.validate(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Check if password is provided (for non-OAuth registration)
        if 'password' not in data or not data['password']:
            return jsonify({
                'success': False,
                'error': 'Password is required'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': data['email']})
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'User with this email already exists'
            }), 409
        
        # Create new user with hashed password
        user_data = {
            'email': data['email'],
            'name': data.get('name', ''),
            'password_hash': hash_password(data['password']),
            'oauth_provider': None,
            'oauth_id': None
        }
        
        user = User(user_data)
        result = users_collection.insert_one(user.to_mongo())
        user._id = result.inserted_id
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_bp.route('/login', methods=['POST'])
def login():
    """
    Login user with email and password
    POST /api/users/login
    Body: {email, password}
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        
        # Find user by email
        user_doc = users_collection.find_one({'email': email})
        
        if not user_doc:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password (1)'
            }), 401
        
        user = User.from_mongo(user_doc)
        
        # Check if user uses OAuth (no password_hash)
        if user.password_hash is None:
            return jsonify({
                'success': False,
                'error': 'This account uses OAuth login'
            }), 401
        
        # Verify password
        password_hash = hash_password(password)
        if password_hash != user.password_hash:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password (2)'
            }), 401
        
        # Update last login time
        users_collection.update_one(
            {'_id': user._id},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_bp.route('/oauth/login', methods=['POST'])
def oauth_login():
    """
    OAuth login endpoint (placeholder for future OAuth integration)
    POST /api/users/oauth/login
    Body: {provider, oauth_id, email, name}
    """
    try:
        data = request.get_json()
        
        provider = data.get('provider')  # e.g., 'google'
        oauth_id = data.get('oauth_id')
        email = data.get('email')
        name = data.get('name', '')
        
        if not all([provider, oauth_id, email]):
            return jsonify({
                'success': False,
                'error': 'Provider, oauth_id, and email are required'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        
        # Check if user exists with this OAuth provider
        user_doc = users_collection.find_one({
            'oauth_provider': provider,
            'oauth_id': oauth_id
        })
        
        if user_doc:
            # Existing OAuth user - update last login
            user = User.from_mongo(user_doc)
            users_collection.update_one(
                {'_id': user._id},
                {'$set': {'last_login': datetime.utcnow()}}
            )
        else:
            # New OAuth user - create account
            user_data = {
                'email': email,
                'name': name,
                'password_hash': None,
                'oauth_provider': provider,
                'oauth_id': oauth_id
            }
            user = User(user_data)
            result = users_collection.insert_one(user.to_mongo())
            user._id = result.inserted_id
        
        return jsonify({
            'success': True,
            'message': 'OAuth login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
