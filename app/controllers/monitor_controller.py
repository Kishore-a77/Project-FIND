from app.services.face_service import detect_faces
from app.services.matching_service import find_best_match


def process_frame(frame, db_embeddings):
    faces = detect_faces(frame)
    results = []

    for face in faces:
        emb = face.embedding
        match = find_best_match(emb, db_embeddings)

        results.append({
            "bbox": face.bbox.astype(int),
            "match": match
        })

    return results
