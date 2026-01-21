import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

# -------------------------------------------------
# Database path
# -------------------------------------------------
DB_PATH = Path("app/db/app.db")


# -------------------------------------------------
# Connection helper
# -------------------------------------------------
def get_connection():
    """
    Returns a SQLite connection with Row factory enabled.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------
# Initialize database (run once)
# -------------------------------------------------
def init_db():
    """
    Creates required tables if they do not exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Missing persons table
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

    # Match logs table
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
# Insert missing person (Day 4)
# -------------------------------------------------
def insert_missing_person(person):
    """
    Stores missing person details and face embedding.
    Embedding is stored as JSON string.
    """
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
# Insert match log (Day 7 / Day 8 / Day 11)
# -------------------------------------------------
def insert_match_log(
    person_id,
    confidence,
    camera_location,
    operator_decision,
    alert_sent=False,
    escalation_level=0
):
    """
    Inserts an audit log for a detected match.
    """
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
# Fetch match logs (Admin / Analytics)
# -------------------------------------------------
def fetch_match_logs(limit=100):
    """
    Fetches recent match logs for admin panel and analytics.
    """
    limit = min(limit, 500)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            LOG_ID,
            PERSON_ID,
            CONFIDENCE,
            CAMERA_LOCATION,
            MATCH_TIME,
            OPERATOR_DECISION,
            ALERT_SENT,
            ESCALATION_LEVEL
        FROM MATCH_LOGS
        ORDER BY MATCH_TIME DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# Fetch all missing persons (Admin / Matching)
# -------------------------------------------------
def fetch_all_missing_persons():
    """
    Returns all registered missing persons.
    """
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
        ORDER BY CREATED_AT DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# Delete missing person (Admin)
# -------------------------------------------------
def delete_missing_person(person_id):
    """
    Deletes a missing person entry by ID.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM MISSING_PERSONS WHERE PERSON_ID = ?",
        (person_id,)
    )

    conn.commit()
    conn.close()
