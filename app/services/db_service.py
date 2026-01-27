import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime

# -------------------------------------------------
# DB path
# -------------------------------------------------
DB_PATH = Path("app/db/app.db")


# -------------------------------------------------
# Connection helper
# -------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------
# Initialize database
# -------------------------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS MISSING_PERSONS (
            PERSON_ID TEXT PRIMARY KEY,
            NAME TEXT NOT NULL,
            AGE INTEGER,
            NOTES TEXT,
            IMAGE_PATH TEXT,
            EMBEDDING TEXT,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS MATCH_LOGS (
            LOG_ID TEXT PRIMARY KEY,
            PERSON_ID TEXT,
            CONFIDENCE REAL,
            CAMERA_LOCATION TEXT,
            MATCH_TIME TIMESTAMP,
            ALERT_SENT INTEGER,
            OPERATOR_DECISION TEXT,
            ESCALATION_LEVEL INTEGER
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# INSERT: Missing Person
# -------------------------------------------------
def insert_missing_person(person):
    conn = get_connection()
    cur = conn.cursor()

    embedding_json = json.dumps(
        person.embedding.tolist()
        if hasattr(person.embedding, "tolist")
        else person.embedding
    )

    cur.execute(
        """
        INSERT INTO MISSING_PERSONS
        (PERSON_ID, NAME, AGE, NOTES, IMAGE_PATH, EMBEDDING)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            person.person_id,
            person.name,
            person.age,
            person.notes,
            person.image_path,
            embedding_json,
        )
    )

    conn.commit()
    conn.close()


# -------------------------------------------------
# INSERT: Match Log (Pending Match)
# -------------------------------------------------
def create_pending_match(
    person_id,
    confidence,
    camera_location,
    alert_sent=False,
    escalation_level=0
):
    """Create a pending match record (for vision_engine.py)"""
    conn = get_connection()
    cur = conn.cursor()
    
    log_id = str(uuid.uuid4())
    
    cur.execute(
        """
        INSERT INTO MATCH_LOGS
        (LOG_ID, PERSON_ID, CONFIDENCE, CAMERA_LOCATION,
         MATCH_TIME, ALERT_SENT, OPERATOR_DECISION, ESCALATION_LEVEL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            log_id,
            person_id,
            confidence,
            camera_location,
            datetime.utcnow(),
            int(alert_sent),
            None,  # operator_decision is NULL for pending matches
            escalation_level,
        )
    )

    conn.commit()
    conn.close()
    return log_id


# -------------------------------------------------
# INSERT: Match Log (General)
# -------------------------------------------------
def insert_match_log(
    person_id,
    confidence,
    camera_location,
    operator_decision=None,
    alert_sent=False,
    escalation_level=0
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO MATCH_LOGS
        (LOG_ID, PERSON_ID, CONFIDENCE, CAMERA_LOCATION,
         MATCH_TIME, ALERT_SENT, OPERATOR_DECISION, ESCALATION_LEVEL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            person_id,
            confidence,
            camera_location,
            datetime.utcnow(),
            int(alert_sent),
            operator_decision,
            escalation_level,
        )
    )

    conn.commit()
    conn.close()


# -------------------------------------------------
# FETCH: All Missing Persons
# -------------------------------------------------
def fetch_all_missing_persons():
    """Fetch all missing persons from database"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            PERSON_ID, 
            NAME, 
            AGE, 
            NOTES, 
            IMAGE_PATH,
            CREATED_AT
        FROM MISSING_PERSONS
        ORDER BY CREATED_AT DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# FETCH: Missing Person by ID
# -------------------------------------------------
def fetch_missing_person_by_id(person_id):
    """Fetch a specific missing person by ID"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            PERSON_ID, 
            NAME, 
            AGE, 
            NOTES, 
            IMAGE_PATH,
            EMBEDDING,
            CREATED_AT
        FROM MISSING_PERSONS
        WHERE PERSON_ID = ?
    """, (person_id,))

    row = cur.fetchone()
    conn.close()
    
    if row:
        # Convert to dict
        return dict(row)
    return None


# -------------------------------------------------
# FETCH: Pending Matches
# -------------------------------------------------
def fetch_pending_matches():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            LOG_ID,
            PERSON_ID,
            CONFIDENCE,
            CAMERA_LOCATION,
            MATCH_TIME,
            ALERT_SENT,
            ESCALATION_LEVEL
        FROM MATCH_LOGS
        WHERE OPERATOR_DECISION IS NULL
        ORDER BY MATCH_TIME DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# FETCH: All Match Logs
# -------------------------------------------------
def fetch_all_match_logs():
    """Fetch all match logs (for admin view)"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            LOG_ID,
            PERSON_ID,
            CONFIDENCE,
            CAMERA_LOCATION,
            MATCH_TIME,
            ALERT_SENT,
            OPERATOR_DECISION,
            ESCALATION_LEVEL
        FROM MATCH_LOGS
        ORDER BY MATCH_TIME DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# DELETE: Missing Person
# -------------------------------------------------
def delete_missing_person(person_id):
    """Delete a missing person record"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM MISSING_PERSONS WHERE PERSON_ID = ?",
        (person_id,)
    )

    conn.commit()
    conn.close()
    return cur.rowcount > 0


# -------------------------------------------------
# UPDATE: Operator Decision
# -------------------------------------------------
def update_match_decision(
    log_id,
    decision,
    alert_sent=False,
    escalation_level=0
):
    """
    Updates human decision on a match.
    decision: 'CONFIRMED' or 'REJECTED'
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE MATCH_LOGS
        SET
            OPERATOR_DECISION = ?,
            ALERT_SENT = ?,
            ESCALATION_LEVEL = ?
        WHERE LOG_ID = ?
        """,
        (
            decision,
            int(alert_sent),
            escalation_level,
            log_id,
        )
    )

    conn.commit()
    conn.close()


# -------------------------------------------------
# COUNT: Statistics
# -------------------------------------------------
def get_statistics():
    """Get system statistics"""
    conn = get_connection()
    cur = conn.cursor()

    # Total missing persons
    cur.execute("SELECT COUNT(*) FROM MISSING_PERSONS")
    total_persons = cur.fetchone()[0]

    # Total matches
    cur.execute("SELECT COUNT(*) FROM MATCH_LOGS")
    total_matches = cur.fetchone()[0]

    # Confirmed matches
    cur.execute("SELECT COUNT(*) FROM MATCH_LOGS WHERE OPERATOR_DECISION = 'CONFIRMED'")
    confirmed_matches = cur.fetchone()[0]

    # Pending matches
    cur.execute("SELECT COUNT(*) FROM MATCH_LOGS WHERE OPERATOR_DECISION IS NULL")
    pending_matches = cur.fetchone()[0]

    conn.close()

    return {
        "total_persons": total_persons,
        "total_matches": total_matches,
        "confirmed_matches": confirmed_matches,
        "pending_matches": pending_matches
    }