from app.services.db_service import (
    fetch_all_missing_persons,
    fetch_all_match_logs,
    delete_missing_person,
    get_statistics
)


def get_missing_persons():
    """Get all missing persons"""
    try:
        return fetch_all_missing_persons()
    except Exception as e:
        print(f"Error fetching missing persons: {e}")
        return []


def get_match_logs():
    """Get all match logs"""
    try:
        return fetch_all_match_logs()
    except Exception as e:
        print(f"Error fetching match logs: {e}")
        return []


def remove_person(person_id):
    """Remove a missing person from database"""
    try:
        return delete_missing_person(person_id)
    except Exception as e:
        print(f"Error deleting person {person_id}: {e}")
        return False


def get_system_stats():
    """Get system statistics"""
    try:
        return get_statistics()
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            "total_persons": 0,
            "total_matches": 0,
            "confirmed_matches": 0,
            "pending_matches": 0
        }