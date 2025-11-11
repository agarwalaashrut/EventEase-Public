"""
Invitations API routes
Handles event invitations and responses
"""
from flask import Blueprint, jsonify, request, current_app
from app.models.user import User
from app.models.event import Event
from datetime import datetime
from bson.objectid import ObjectId

invitations_bp = Blueprint('invitations', __name__, url_prefix='/api/invitations')


def get_db():
    """Get database connection from current app"""
    return current_app.db


@invitations_bp.route('', methods=['GET'])
def get_user_invitations():
    """
    Get all invitations for a user
    GET /api/invitations?email=user@example.com
    Query params: email (required)
    """
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email parameter is required'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        events_collection = db['Events']
        
        # Find user
        user_doc = users_collection.find_one({'email': email})
        if not user_doc:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = User.from_mongo(user_doc)
        
        # Get event details for each invitation
        invitations = []
        for event_id in user.invitations:
            try:
                event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
                if event_doc:
                    event = Event.from_mongo(event_doc)
                    invitations.append({
                        'event_id': event_id,
                        'event': event.to_dict()
                    })
            except Exception:
                # Skip invalid event IDs
                continue
        
        return jsonify({
            'success': True,
            'count': len(invitations),
            'invitations': invitations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@invitations_bp.route('/<invitation_id>/respond', methods=['POST'])
def respond_to_invitation(invitation_id):
    """
    Respond to an invitation (accept/decline)
    POST /api/invitations/<event_id>/respond
    Body: {email, response}
    response: "accepted" or "declined"
    """
    try:
        from app.services.email_service import send_response_notification
        
        data = request.get_json()
        email = data.get('email')
        response = data.get('response')
        
        if not email or not response:
            return jsonify({
                'success': False,
                'error': 'Email and response are required'
            }), 400
        
        if response not in ['accepted', 'declined']:
            return jsonify({
                'success': False,
                'error': 'Response must be "accepted" or "declined"'
            }), 400
        
        db = get_db()
        users_collection = db['Users']
        events_collection = db['Events']
        
        # Verify invitation exists
        user_doc = users_collection.find_one({'email': email})
        if not user_doc:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = User.from_mongo(user_doc)
        
        if invitation_id not in user.invitations:
            return jsonify({
                'success': False,
                'error': 'Invitation not found'
            }), 404
        
        # Get event details for notification
        event_doc = events_collection.find_one({'_id': ObjectId(invitation_id)})
        
        # Remove invitation from user's list
        users_collection.update_one(
            {'email': email},
            {'$pull': {'invitations': invitation_id}}
        )
        
        # If accepted, add user to event attendees
        if response == 'accepted':
            events_collection.update_one(
                {'_id': ObjectId(invitation_id)},
                {'$addToSet': {'attendees': email}}
            )
        
        # Send notification email to organizer
        if event_doc:
            send_response_notification(
                event_doc.get('organizer_email'),
                user_doc.get('name', 'A user'),
                email,
                event_doc.get('title'),
                response
            )
        
        return jsonify({
            'success': True,
            'message': f'Invitation {response}',
            'response': response
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
