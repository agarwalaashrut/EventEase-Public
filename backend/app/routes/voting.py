"""
Voting API routes
Handles voting operations for events
"""
from flask import Blueprint, jsonify, request
from app.models.event import Event
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

voting_bp = Blueprint('voting', __name__, url_prefix='/api/events')


def get_db():
    """Get database connection"""
    mongo_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('DB_NAME', 'Main_Events')
    client = MongoClient(mongo_uri)
    return client[db_name]


@voting_bp.route('/<event_id>/vote', methods=['POST'])
def submit_vote(event_id):
    """
    Submit votes for time slots
    POST /api/events/<event_id>/vote
    Body: {user_email, time_slot_indexes: [0, 2]}
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('user_email'):
            return jsonify({
                'success': False,
                'error': 'Missing required field: user_email'
            }), 400
        
        if 'time_slot_indexes' not in data or not isinstance(data.get('time_slot_indexes'), list):
            return jsonify({
                'success': False,
                'error': 'Missing required field: time_slot_indexes (must be a list)'
            }), 400
        
        user_email = data.get('user_email')
        time_slot_indexes = data.get('time_slot_indexes')
        
        db = get_db()
        events_collection = db['Events']
        
        # Find event
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Create Event object and add vote
        event = Event.from_mongo(event_doc)
        event.add_vote(user_email, time_slot_indexes)
        
        # Update event in database
        events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': {'votes': event.votes}}
        )
        
        return jsonify({
            'success': True,
            'message': 'Vote submitted successfully',
            'votes': event.votes
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voting_bp.route('/<event_id>/votes', methods=['GET'])
def get_voting_results(event_id):
    """
    Get voting results for an event
    GET /api/events/<event_id>/votes
    """
    try:
        db = get_db()
        events_collection = db['Events']
        
        # Find event
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Create Event object to use aggregation methods
        event = Event.from_mongo(event_doc)
        
        # Get vote aggregation and most popular slots
        vote_aggregation = event.get_vote_aggregation()
        popular_slots = event.get_most_popular_time_slots()
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'votes_by_user': event.votes,
            'votes_by_time_slot': vote_aggregation,
            'popular_time_slots': [
                {
                    'time_slot_index': slot[0],
                    'vote_count': slot[1],
                    'time_slot': event.proposed_times[slot[0]] if slot[0] < len(event.proposed_times) else None
                }
                for slot in popular_slots
            ],
            'total_votes': sum(vote_aggregation.values()),
            'total_participants': len(event.votes),
            'proposed_times': event.proposed_times
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@voting_bp.route('/<event_id>/finalize', methods=['POST'])
def finalize_event(event_id):
    """
    Finalize event with the winning time slot
    POST /api/events/<event_id>/finalize
    Body: {time_slot_index} (optional - if not provided, uses most voted)
    """
    try:
        data = request.get_json() or {}
        
        db = get_db()
        events_collection = db['Events']
        
        # Find event
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Create Event object
        event = Event.from_mongo(event_doc)
        
        # Determine winning time slot
        if 'time_slot_index' in data and data['time_slot_index'] is not None:
            winning_index = data['time_slot_index']
            # Validate the index
            if not isinstance(winning_index, int) or winning_index < 0 or winning_index >= len(event.proposed_times):
                return jsonify({
                    'success': False,
                    'error': 'Invalid time_slot_index'
                }), 400
        else:
            # Use the most voted time slot
            winning_index = event.get_winning_time_slot()
            if winning_index is None:
                return jsonify({
                    'success': False,
                    'error': 'No votes yet. Cannot finalize without votes or explicit time_slot_index.'
                }), 400
        
        # Update event
        event.finalized_time_slot = winning_index
        event.status = 'confirmed'
        
        # Update in database
        events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {
                '$set': {
                    'finalized_time_slot': event.finalized_time_slot,
                    'status': event.status
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Event finalized successfully',
            'finalized_time_slot_index': winning_index,
            'finalized_time_slot': event.proposed_times[winning_index],
            'event': event.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
