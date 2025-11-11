"""
Event model for managing event data
Defines the structure and validation for Event documents in MongoDB
"""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bson import ObjectId


class Event:
    """Event model representing a proposed event with voting capabilities"""
    
    def __init__(self, data: dict):
        """Initialize Event from dictionary data"""
        self._id = data.get('_id')
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.organizer = data.get('organizer', '')
        self.organizer_email = data.get('organizer_email', '')
        self.location = data.get('location', '')
        self.proposed_times = data.get('proposed_times', [])
        self.attendees = data.get('attendees', [])
        self.status = data.get('status', 'pending')  # pending, confirmed, cancelled
        self.created_at = data.get('created_at', datetime.utcnow())
        self.votes = data.get('votes', {})  # {email: [time_slot_indexes]}
        self.invites = data.get('invites', [])  # List of UserIDs
        self.finalized_time_slot = data.get('finalized_time_slot', None)
        
    def add_vote(self, user_email: str, time_slot_indexes: List[int]) -> None:
        """
        Add or update a vote for a user
        Args:
            user_email: Email of the user voting
            time_slot_indexes: List of indices of preferred time slots
        """
        self.votes[user_email] = time_slot_indexes
    
    def get_vote_aggregation(self) -> Dict[int, int]:
        """
        Aggregate votes and count votes per time slot
        Returns: {time_slot_index: vote_count}
        """
        time_slot_votes = {}
        
        for user_email, indexes in self.votes.items():
            for index in indexes:
                time_slot_votes[index] = time_slot_votes.get(index, 0) + 1
        
        return time_slot_votes
    
    def get_most_popular_time_slots(self) -> List[Tuple[int, int]]:
        """
        Determine the most popular time slots based on votes
        Returns: List of (time_slot_index, vote_count) tuples sorted by vote count descending
        """
        aggregation = self.get_vote_aggregation()
        
        if not aggregation:
            return []
        
        # Sort by vote count descending, then by index ascending
        sorted_slots = sorted(aggregation.items(), key=lambda x: (-x[1], x[0]))
        return sorted_slots
    
    def get_winning_time_slot(self) -> Optional[int]:
        """
        Get the time slot with the most votes
        Returns: time_slot_index of the winning time slot, or None if no votes
        """
        popular = self.get_most_popular_time_slots()
        return popular[0][0] if popular else None
        
    
    def to_dict(self) -> dict:
        """Convert Event to dictionary for JSON serialization"""
        return {
            '_id': str(self._id) if self._id else None,
            'title': self.title,
            'description': self.description,
            'organizer': self.organizer,
            'organizer_email': self.organizer_email,
            'location': self.location,
            'proposed_times': self.proposed_times,
            'attendees': self.attendees,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'votes': self.votes,
            'invites': self.invites,
            'finalized_time_slot': self.finalized_time_slot
        }
    
    def to_mongo(self) -> dict:
        """Convert Event to MongoDB document format"""
        doc = {
            'title': self.title,
            'description': self.description,
            'organizer': self.organizer,
            'organizer_email': self.organizer_email,
            'location': self.location,
            'proposed_times': self.proposed_times,
            'attendees': self.attendees,
            'status': self.status,
            'created_at': self.created_at,
            'votes': self.votes,
            'invites': self.invites,
            'finalized_time_slot': self.finalized_time_slot
        }
        if self._id:
            doc['_id'] = self._id
        return doc
    
    @staticmethod
    def from_mongo(doc: dict) -> 'Event':
        """Create Event instance from MongoDB document"""
        if doc is None:
            return None
        return Event(doc)
    
    @staticmethod
    def validate(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate event data
        Returns: (is_valid, error_message)
        """
        required_fields = ['title', 'organizer_email', 'location']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        if not isinstance(data.get('proposed_times', []), list):
            return False, "proposed_times must be a list"
        
        if not isinstance(data.get('attendees', []), list):
            return False, "attendees must be a list"
        
        return True, None
