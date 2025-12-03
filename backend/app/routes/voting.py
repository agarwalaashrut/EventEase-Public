"""
Voting API routes
Handles voting operations for events
"""
from flask import Blueprint, jsonify, request
from app.models.event import Event
from app.services.voting_service import (
    calculate_tallies,
    handle_vote_conflict,
    determine_winner,
)
from app.services.calendar_service import get_calendar_service
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
    Submit a vote for a single time slot
    POST /api/events/<event_id>/vote
    Body: {user_email, time_slot_index: 0}
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('user_email'):
            return jsonify({
                'success': False,
                'error': 'Missing required field: user_email'
            }), 400
        
        if 'time_slot_index' not in data or not isinstance(data.get('time_slot_index'), int):
            return jsonify({
                'success': False,
                'error': 'Missing required field: time_slot_index (must be an integer)'
            }), 400
        
        user_email = data.get('user_email')
        time_slot_index = data.get('time_slot_index')
        
        db = get_db()
        events_collection = db['Events']
        
        # Find event
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Validate time slot index
        proposed_times = event_doc.get('proposed_times', []) or []
        if time_slot_index < 0 or time_slot_index >= len(proposed_times):
            return jsonify({
                'success': False,
                'error': 'Invalid time_slot_index'
            }), 400
        
        # Handle conflict: merge incoming vote with existing votes (replace strategy)
        existing_votes = event_doc.get('votes', {}) or {}
        merged_votes = handle_vote_conflict(
            existing_votes, 
            {user_email: time_slot_index}, 
            strategy="replace"
        )
        
        # Persist merged votes to database
        events_collection.update_one(
            {'_id': ObjectId(event_id)},
            {'$set': {'votes': merged_votes}}
        )
        
        # Calculate tallies for response
        num_slots = len(proposed_times)
        tallies = calculate_tallies(merged_votes, num_slots=num_slots if num_slots > 0 else None)
        
        return jsonify({
            'success': True,
            'message': 'Vote submitted successfully',
            'votes': merged_votes,
            'tallies': tallies
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
        
        # Extract votes and proposed times
        votes = event_doc.get('votes', {}) or {}
        proposed_times = event_doc.get('proposed_times', []) or []
        num_slots = len(proposed_times)
        
        # Calculate tallies using service
        tallies = calculate_tallies(votes, num_slots=num_slots if num_slots > 0 else None)
        
        # Determine winner using service
        winner, winner_context = determine_winner(
            votes, 
            num_slots=num_slots if num_slots > 0 else None
        )
        
        # Build popular slots list (sorted by votes desc, index asc)
        popular_slots = sorted(tallies.items(), key=lambda x: (-x[1], x[0]))
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'votes_by_user': votes,
            'votes_by_time_slot': tallies,
            'popular_time_slots': [
                {
                    'time_slot_index': slot[0],
                    'vote_count': slot[1],
                    'time_slot': proposed_times[slot[0]] if slot[0] < len(proposed_times) else None
                }
                for slot in popular_slots
            ],
            'winner': winner,
            'winner_context': winner_context,
            'total_votes': sum(tallies.values()),
            'total_participants': len(votes),
            'proposed_times': proposed_times
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
    If organizer has Google Calendar connected, creates event on their calendar
    POST /api/events/<event_id>/finalize
    Body: {time_slot_index} (optional - if not provided, uses most voted)
    """
    try:
        data = request.get_json() or {}
        
        db = get_db()
        events_collection = db['Events']
        users_collection = db['Users']
        
        # Find event
        event_doc = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_doc:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
        
        # Create Event object
        event = Event.from_mongo(event_doc)
        
        # Determine winning time slot: explicit index or service-determined
        if 'time_slot_index' in data and data['time_slot_index'] is not None:
            winning_index = data['time_slot_index']
            # Validate the index
            if not isinstance(winning_index, int) or winning_index < 0 or winning_index >= len(event.proposed_times):
                return jsonify({
                    'success': False,
                    'error': 'Invalid time_slot_index'
                }), 400
        else:
            # Use service to determine winner
            votes = event_doc.get('votes', {}) or {}
            num_slots = len(event.proposed_times)
            winning_index, ctx = determine_winner(
                votes, 
                num_slots=num_slots if num_slots > 0 else None
            )
            if winning_index is None:
                return jsonify({
                    'success': False,
                    'error': 'No clear winning time slot. Please provide time_slot_index or ensure votes exist.',
                    'context': ctx
                }), 400
        
        # Update event
        event.finalized_time_slot = winning_index
        event.status = 'confirmed'
        finalized_time = event.proposed_times[winning_index]
        
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
        
        # Attempt to create calendar event if organizer has Google Calendar connected
        calendar_response = {
            'calendar_event_created': False,
            'calendar_event_id': None,
            'calendar_error': None
        }
        
        try:
            organizer_doc = users_collection.find_one({'email': event.organizer_email})
            if organizer_doc and organizer_doc.get('google_refresh_token'):
                calendar_service = get_calendar_service()
                
                # Prepare attendee emails
                attendee_emails = event.attendees if event.attendees else []
                if event.organizer_email not in attendee_emails:
                    attendee_emails = [event.organizer_email] + attendee_emails
                
                # Create calendar event
                success, cal_event_id, error = calendar_service.create_calendar_event(
                    refresh_token=organizer_doc['google_refresh_token'],
                    event_title=event.title,
                    event_time=finalized_time,
                    event_description=event.description or '',
                    organizer_email=event.organizer_email,
                    attendee_emails=attendee_emails
                )
                
                if success:
                    calendar_response['calendar_event_created'] = True
                    calendar_response['calendar_event_id'] = cal_event_id
                    
                    # Store calendar event ID in event document
                    events_collection.update_one(
                        {'_id': ObjectId(event_id)},
                        {'$set': {'google_calendar_event_id': cal_event_id}}
                    )
                else:
                    calendar_response['calendar_error'] = error
        except Exception as cal_error:
            calendar_response['calendar_error'] = f"Calendar sync error: {str(cal_error)}"
        
        return jsonify({
            'success': True,
            'message': 'Event finalized successfully',
            'finalized_time_slot_index': winning_index,
            'finalized_time_slot': finalized_time,
            'event': event.to_dict(),
            'calendar': calendar_response
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
