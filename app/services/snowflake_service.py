# pyright: ignore

import json
import uuid
from datetime import datetime

import streamlit as st
import snowflake.connector



# -------------------------------------------------
# Snowflake connection (SECURE)
# -------------------------------------------------
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"],
    )


# -------------------------------------------------
# Insert missing person (Day 4)
# -------------------------------------------------
def insert_missing_person(person):
    conn = get_connection()
    cur = conn.cursor()

    # Ensure numpy arrays are converted to native lists for JSON serialization
    embedding_json = json.dumps(
        person.embedding.tolist() if hasattr(person.embedding, "tolist") else person.embedding
    )

    cur.execute(
        """
        INSERT INTO CORE.MISSING_PERSONS
        (PERSON_ID, NAME, AGE, NOTES, IMAGE_PATH, EMBEDDING)
        SELECT %s, %s, %s, %s, %s, PARSE_JSON(%s)
        """,
        (
            person.person_id,
            person.name,
            person.age,
            person.notes,
            person.image_path,
            embedding_json,
        ),
    )

    cur.close()
    conn.close()


# -------------------------------------------------
# Fetch persons (monitoring + admin)
# -------------------------------------------------
def fetch_all_persons_with_images():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT PERSON_ID, NAME, IMAGE_PATH, EMBEDDING
        FROM CORE.MISSING_PERSONS
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_all_missing_persons():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT PERSON_ID, NAME, AGE, NOTES, IMAGE_PATH, CREATED_AT
        FROM CORE.MISSING_PERSONS
        ORDER BY CREATED_AT DESC
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# -------------------------------------------------
# Match logs (Day 7–9)
# -------------------------------------------------
def insert_match_log(
    person_id,
    confidence,
    camera_location,
    operator_decision,
    alert_sent=False,
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO CORE.MATCH_LOGS
        (LOG_ID, PERSON_ID, CONFIDENCE, CAMERA_LOCATION,
         MATCH_TIME, ALERT_SENT, OPERATOR_DECISION)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            str(uuid.uuid4()),
            person_id,
            confidence,
            camera_location,
            datetime.utcnow(),
            alert_sent,
            operator_decision,
        ),
    )

    cur.close()
    conn.close()


def update_alert_sent(log_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE CORE.MATCH_LOGS
        SET ALERT_SENT = TRUE
        WHERE LOG_ID = %s
        """,
        (log_id,),
    )

    cur.close()
    conn.close()


def fetch_match_logs(limit=100):
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
            ALERT_SENT
        FROM CORE.MATCH_LOGS
        ORDER BY MATCH_TIME DESC
        LIMIT %s
        """,
        (limit,),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# -------------------------------------------------
# Admin delete functions
# -------------------------------------------------
def delete_missing_person(person_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM CORE.MISSING_PERSONS
        WHERE PERSON_ID = %s
        """,
        (person_id,),
    )

    cur.close()
    conn.close()


def delete_match_logs_for_person(person_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM CORE.MATCH_LOGS
        WHERE PERSON_ID = %s
        """,
        (person_id,),
    )

    cur.close()
    conn.close()
