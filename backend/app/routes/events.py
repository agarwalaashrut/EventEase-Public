"""
Events API routes
Handles CRUD operations for events
"""
from flask import Blueprint, jsonify, request
from app.models.event import Event
from pymongo import MongoClient
import os

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

# MongoDB connection
def get_db():
    """Get database connection"""
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'Main_Events')
    client = MongoClient(mongo_uri)
    return client[db_name]


@events_bp.route('', methods=['GET'])
def get_all_events():
    """
    Get all events
    GET /api/events
    """
    try:
        db = get_db()
        events_collection = db['Events']
        
        # Fetch all events from MongoDB
        events_docs = list(events_collection.find({}))
        
        # Convert to Event objects and then to dictionaries
        events = [Event.from_mongo(doc).to_dict() for doc in events_docs]
        
        return jsonify({
            'success': True,
            'count': len(events),
            'events': events
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@events_bp.route('/<event_id>', methods=['GET'])
def get_event(event_id):
    """
    Get a single event by ID
    GET /api/events/<event_id>
    """
    try:
        from bson.objectid import ObjectId
        
        db = get_db()
        events_collection = db['Events']
        
        # Find event by ID
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        event = Event.from_mongo(event_doc)
        
        return jsonify({
            'success': True,
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@events_bp.route('', methods=['POST'])
def create_event():
    """
    Create a new event
    POST /api/events
    Body: {title, description, organizer, organizer_email, location, proposed_times, attendees}
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = Event.validate(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Create event
        event = Event(data)
        
        db = get_db()
        events_collection = db['Events']
        
        # Insert into MongoDB
        result = events_collection.insert_one(event.to_mongo())
        event._id = result.inserted_id
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@events_bp.route('/<event_id>/invite', methods=['POST'])
def invite_to_event(event_id):
    """
    Send invitations to users for an event
    POST /api/events/<event_id>/invite
    Body: {emails: ["user1@example.com", "user2@example.com"]}
    """
    try:
        from bson.objectid import ObjectId
        
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails or not isinstance(emails, list):
            return jsonify({
                'success': False,
                'error': 'emails array is required'
            }), 400
        
        db = get_db()
        events_collection = db['Events']
        users_collection = db['Users']
        
        # Verify event exists
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        invited_users = []
        not_found_emails = []
        
        # Add invitation to each user
        for email in emails:
            user = users_collection.find_one({'email': email})
            
            if not user:
                not_found_emails.append(email)
                continue
            
            # Create invitation object
            invitation = {
                'event_id': str(event_doc['_id']),
                'event_title': event_doc['title'],
                'organizer': event_doc['organizer'],
                'status': 'pending',
                'invited_at': Event.get_timestamp()
            }
            
            # Add to user's invitations if not already invited
            existing_invitation = next(
                (inv for inv in user.get('invitations', []) 
                 if inv['event_id'] == str(event_doc['_id'])),
                None
            )
            
            if not existing_invitation:
                users_collection.update_one(
                    {'_id': user['_id']},
                    {'$push': {'invitations': invitation}}
                )
                invited_users.append(email)
        
        return jsonify({
            'success': True,
            'message': f'Invited {len(invited_users)} users',
            'invited': invited_users,
            'not_found': not_found_emails
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@events_bp.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
    """
    Update an existing event
    PUT /api/events/<event_id>
    """
    try:
        from bson.objectid import ObjectId
        
        data = request.get_json()
        
        db = get_db()
        events_collection = db['Events']
        
        # Update event
        result = events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Fetch updated event
        updated_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        event = Event.from_mongo(updated_doc)
        
        return jsonify({
            'success': True,
            'message': 'Event updated successfully',
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@events_bp.route('/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """
    Delete an event
    DELETE /api/events/<event_id>
    """
    try:
        from bson.objectid import ObjectId
        
        db = get_db()
        events_collection = db['Events']
        
        result = events_collection.delete_one({'_id': ObjectId(event_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
