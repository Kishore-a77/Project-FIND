import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.face_service import get_face_embedding, compare_faces

emb1 = get_face_embedding("app/data/test_faces/person1.jpg")
emb2 = get_face_embedding("app/data/test_faces/person1_2.jpg")
emb3 = get_face_embedding("app/data/test_faces/person2.jpg")

print("Same person similarity:", compare_faces(emb1, emb2))
print("Different person similarity:", compare_faces(emb1, emb3))
