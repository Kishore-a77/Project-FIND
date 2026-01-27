import os
import uuid
from pathlib import Path

# Try to import MissingPerson model
try:
    from app.models.person_model import MissingPerson
    HAS_MODEL = True
except ImportError:
    # Create a simple class if model doesn't exist
    class MissingPerson:
        def __init__(self, person_id, name, age, notes, image_path, embedding):
            self.person_id = person_id
            self.name = name
            self.age = age
            self.notes = notes
            self.image_path = image_path
            self.embedding = embedding
    HAS_MODEL = False

from app.services.face_service import get_face_embedding
from app.services.db_service import insert_missing_person

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("app/data/uploaded_faces")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def handle_report(name, age, notes, uploaded_file):
    """
    Handle missing person report submission
    
    Args:
        name: Person's name
        age: Person's age
        notes: Additional notes
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        person_id: Generated unique ID for the person
        
    Raises:
        ValueError: If face detection fails
        Exception: For other errors
    """
    try:
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Name is required")
        
        if not uploaded_file:
            raise ValueError("Photo is required")
        
        # Generate unique ID
        person_id = str(uuid.uuid4())
        
        # Save image to upload directory
        image_path = UPLOAD_DIR / f"{person_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Generate face embedding
            embedding = get_face_embedding(str(image_path))
            
            # Convert embedding to list for storage
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            
            # Create model object
            person = MissingPerson(
                person_id=person_id,
                name=name.strip(),
                age=int(age) if age else 0,
                notes=notes.strip() if notes else "",
                image_path=str(image_path),
                embedding=embedding_list
            )
            
            # Store in database
            insert_missing_person(person)
            
            return person_id
            
        except Exception as e:
            # Clean up saved image if embedding failed
            if image_path.exists():
                image_path.unlink()
            raise e
            
    except ValueError as e:
        # Re-raise face detection errors
        raise ValueError(f"Face detection failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to process report: {str(e)}")