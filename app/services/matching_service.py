# app/services/matching_service.py
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_THRESHOLD = 0.45  # webcam-friendly


def _normalize(vec: np.ndarray) -> np.ndarray:
    """L2 normalize embedding safely."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def parse_embedding(embedding):
    """
    Convert embedding to float32 numpy array.
    Accepts: np.ndarray | list | JSON string
    Never raises inside live loop.
    """
    try:
        if embedding is None:
            return None

        if isinstance(embedding, np.ndarray):
            return embedding.astype("float32")

        if isinstance(embedding, list):
            return np.array(embedding, dtype="float32")

        if isinstance(embedding, str):
            embedding = embedding.strip()
            if not embedding:
                return None
            return np.array(json.loads(embedding), dtype="float32")

    except Exception:
        return None

    return None


def find_best_match(live_embedding, db_embeddings, threshold=DEFAULT_THRESHOLD):
    """
    live_embedding: np.ndarray (512,)
    db_embeddings: list of dicts:
        {
            person_id,
            name,
            embedding (np.ndarray)
        }
    """

    if live_embedding is None or not db_embeddings:
        return None

    q = parse_embedding(live_embedding)
    if q is None:
        return None

    q = _normalize(q).reshape(1, -1)

    best_score = 0.0
    best_person = None

    for person in db_embeddings:
        db_emb = parse_embedding(person.get("embedding"))
        if db_emb is None:
            continue

        d = _normalize(db_emb).reshape(1, -1)

        score = cosine_similarity(q, d)[0][0]

        if score > best_score:
            best_score = score
            best_person = person

    if best_person and best_score >= threshold:
        return {
            "person_id": best_person["person_id"],
            "name": best_person["name"],
            "score": float(round(best_score, 4)),
        }

    return None
