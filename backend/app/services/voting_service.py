"""
Voting business logic for EventEase.

This module provides core voting functionality:
- Calculate vote tallies per time slot
- Handle vote conflicts with configurable merge strategies
- Determine consensus / winning time slot with tie-breaking

Voting model: votes = { "user_email": time_slot_index }  (single vote per user)
"""
from typing import Dict, List, Optional, Tuple


def calculate_tallies(
    votes: Dict[str, int], num_slots: Optional[int] = None
) -> Dict[int, int]:
    """
    Calculate vote tallies per time slot.

    Args:
        votes: Dict mapping user_email -> time slot index (single vote per user)
        num_slots: Optional upper bound; indices >= num_slots are ignored

    Returns:
        Dict mapping time_slot_index -> vote_count
    """
    tallies: Dict[int, int] = {}

    if not votes:
        return tallies

    for user_email, slot_idx in votes.items():
        if not isinstance(slot_idx, int):
            continue
        if num_slots is not None and (slot_idx < 0 or slot_idx >= num_slots):
            continue
        tallies[slot_idx] = tallies.get(slot_idx, 0) + 1

    return tallies


def handle_vote_conflict(
    existing: Dict[str, int],
    incoming: Dict[str, int],
    strategy: str = "replace",
) -> Dict[str, int]:
    """
    Handle vote conflicts when a user submits a new vote.

    Args:
        existing: Current votes dict (user_email -> slot_index)
        incoming: New votes to merge (single vote per user)
        strategy: Merge strategy:
            - "replace": incoming vote replaces existing (default)
            - "ignore": keep existing if user already voted

    Returns:
        Merged votes dict
    """
    if existing is None:
        existing = {}
    if incoming is None:
        return dict(existing)

    merged = dict(existing)

    for user_email, slot_idx in incoming.items():
        if not isinstance(slot_idx, int):
            continue

        if strategy == "replace":
            merged[user_email] = slot_idx
        elif strategy == "ignore":
            if user_email not in merged:
                merged[user_email] = slot_idx
        else:
            # fallback to replace
            merged[user_email] = slot_idx

    return merged


def resolve_ties(tallies: Dict[int, int]) -> List[int]:
    """
    Find all time slots tied for the most votes.

    Args:
        tallies: Dict mapping time_slot_index -> vote_count

    Returns:
        Sorted list of tied time slot indices
    """
    if not tallies:
        return []
    max_votes = max(tallies.values())
    return sorted([idx for idx, cnt in tallies.items() if cnt == max_votes])


def determine_winner(
    votes: Dict[str, int],
    num_slots: Optional[int] = None,
    require_majority: bool = False,
) -> Tuple[Optional[int], Dict]:
    """
    Determine the winning time slot from votes.

    Args:
        votes: Dict mapping user_email -> time slot index (single vote per user)
        num_slots: Optional upper bound for validation
        require_majority: If True, winner must have >50% of participants

    Returns:
        Tuple of (winner_index_or_None, context_dict)
        context includes: tallies, candidates, total_participants, total_votes, reason
    """
    tallies = calculate_tallies(votes, num_slots=num_slots)
    total_participants = len(votes) if votes else 0
    total_votes = sum(tallies.values())

    if not tallies:
        return None, {"reason": "no_votes", "tallies": tallies}

    candidates = resolve_ties(tallies)

    context = {
        "tallies": tallies,
        "candidates": candidates,
        "total_participants": total_participants,
        "total_votes": total_votes,
    }

    # Single candidate: clear winner
    if len(candidates) == 1:
        return candidates[0], context

    # Multiple candidates (tie)
    if require_majority:
        for c in candidates:
            if tallies.get(c, 0) > (total_participants / 2):
                context["reason"] = "majority"
                return c, context
        context["reason"] = "no_majority"
        return None, context

    # Deterministic tie-break: choose lowest index
    winner = min(candidates)
    context["reason"] = "tie_broken_by_lowest_index"
    return winner, context
