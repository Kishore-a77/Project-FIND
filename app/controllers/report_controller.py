import os
import uuid
import numpy as np
from app.models.person_model import MissingPerson
from app.services.face_service import get_face_embedding
from app.services.snowflake_service import insert_missing_person

UPLOAD_DIR = "app/data/uploaded_faces"


def handle_report(name, age, notes, uploaded_file):
    # Generate unique ID
    person_id = str(uuid.uuid4())

    # Save image
    image_path = os.path.join(UPLOAD_DIR, f"{person_id}.jpg")
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Generate face embedding
    embedding = get_face_embedding(image_path)
    embedding_list = embedding.tolist()  # Snowflake-friendly

    # Create model object
    person = MissingPerson(
        person_id=person_id,
        name=name,
        age=age,
        notes=notes,
        image_path=image_path,
        embedding=embedding_list
    )

    # Store in Snowflake
    insert_missing_person(person)

    return person_id
