from app.services.snowflake_service import (
    fetch_all_missing_persons,
    fetch_match_logs,
    delete_missing_person
)

def get_missing_persons():
    return fetch_all_missing_persons()

def get_match_logs():
    return fetch_match_logs()

def remove_person(person_id):
    delete_missing_person(person_id)
