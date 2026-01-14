"""
Authentication routes for OAuth integration
Handles Google Calendar OAuth flow
"""
from flask import Blueprint, request, jsonify, session, current_app, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import uuid
import json
from app.models.user import User
from app.services.calendar_service import get_calendar_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
oauth_bp = Blueprint('oauth', __name__)


def get_db():
    """Get database connection"""
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'Main_Events')
    client = MongoClient(mongo_uri)
    return client[db_name]


@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    print("HIT /api/auth/google/login")
    """
    Initiate Google OAuth flow
    Generates OAuth URL and stores state in session for CSRF protection
    
    GET /api/auth/google/login
    Query params:
        - redirect_url (optional): Frontend URL to redirect to after auth (default: http://localhost:3000)
    
    Returns:
        { success: true, auth_url: "https://accounts.google.com/o/oauth2/auth?..." }
    """
    try:
        # Generate CSRF state token
        state = str(uuid.uuid4())
        redirect_url = os.getenv("GOOGLE_REDIRECT_URI")
        
        # Store state and redirect_url in session (backend managed)
        # In production, consider using Redis for better scalability
        session[f'oauth_state_{state}'] = {
            'created_at': os.environ.get('TIMESTAMP', ''),
            'redirect_url': redirect_url
        }
        print("GOOGLE_REDIRECT_URI =", repr(redirect_url))
        # Get OAuth URL
        calendar_service = get_calendar_service()
        auth_url = calendar_service.get_auth_url(state)
        print("AUTH URL SENT TO FRONTEND:")
        print(auth_url)
        return jsonify({
            'success': True,
            'auth_url': auth_url,
            'state': state
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@oauth_bp.route('/oauth2callback', methods=['GET'])
def google_callback():
    """
    Google OAuth callback endpoint
    Exchanges authorization code for tokens, stores in database, and redirects to home page
    
    GET /oauth2callback
    Query params:
        - code: Authorization code from Google
        - state: CSRF state token (should match stored state)
    
    Redirects to home page with user_id and email in query params
    """
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Handle user denial
        if error:
            return redirect(f'http://localhost:3000?auth=cancelled&error={error}')
        
        if not code or not state:
            return redirect('http://localhost:3000?auth=failed&error=missing_code_or_state')
        
        # Verify state token (CSRF protection)
        state_data = session.pop(f'oauth_state_{state}', None)
        if not state_data:
            return redirect('http://localhost:3000?auth=failed&error=invalid_state')
        
        # Exchange code for tokens
        calendar_service = get_calendar_service()
        creds_dict, access_token = calendar_service.get_credentials_from_code(code)
        
        # Extract user info from token
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        credentials = Credentials(token=access_token)
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        user_email = user_info.get('email')
        user_name = user_info.get('name', user_email.split('@')[0])
        
        # Find or create user in database
        db = get_db()
        users_collection = db['Users']
        
        user_doc = users_collection.find_one({'email': user_email})
        
        if user_doc:
            # Update existing user with Google credentials
            users_collection.update_one(
                {'email': user_email},
                {
                    '$set': {
                        'google_refresh_token': creds_dict.get('refresh_token'),
                        'google_calendar_id': user_email,
                        'oauth_provider': 'google',
                        'oauth_id': user_info.get('id')
                    }
                }
            )
            user = User.from_mongo(users_collection.find_one({'email': user_email}))
        else:
            # Create new user
            new_user = User({
                'email': user_email,
                'name': user_name,
                'oauth_provider': 'google',
                'oauth_id': user_info.get('id'),
                'google_refresh_token': creds_dict.get('refresh_token'),
                'google_calendar_id': user_email,
                'password_hash': None,
                'invitations': []
            })
            result = users_collection.insert_one(new_user.to_mongo())
            new_user._id = result.inserted_id
            user = new_user
        
        # Redirect to home page with user info
        user_id = str(user._id)
        redirect_url = f'http://localhost:3000?auth=success&user_id={user_id}&email={user_email}'
        
        return redirect(redirect_url)
        
    except Exception as e:
        error_msg = str(e).replace(' ', '%20')
        return redirect(f'http://localhost:3000?auth=failed&error={error_msg}')


@auth_bp.route('/calendar/status', methods=['GET'])
def get_calendar_status():
    """
    Check if user has connected their Google Calendar
    
    GET /api/auth/calendar/status?email=user@example.com
    Query params:
        - email: User email address
    
    Returns:
        {
            success: true,
            calendar_connected: true,
            calendar_id: "user@example.com"
        }
    """
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Missing email parameter'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        
        user_doc = users_collection.find_one({'email': email})
        
        if not user_doc:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = User.from_mongo(user_doc)
        
        return jsonify({
            'success': True,
            'calendar_connected': bool(user.google_refresh_token),
            'calendar_id': user.google_calendar_id,
            'user_id': str(user._id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/calendar/disconnect', methods=['POST'])
def disconnect_calendar():
    """
    Disconnect Google Calendar from user account
    
    POST /api/auth/calendar/disconnect
    Body: { email: "user@example.com" }
    
    Returns:
        { success: true, message: "Calendar disconnected" }
    """
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Missing email field'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        
        result = users_collection.update_one(
            {'email': email},
            {
                '$set': {
                    'google_refresh_token': None,
                    'google_calendar_id': None
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Calendar disconnected successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
