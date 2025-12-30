import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity

THRESHOLD_STRONG = 0.80
THRESHOLD_WEAK = 0.65


def parse_embedding(embedding):
    if isinstance(embedding, str):
        embedding = json.loads(embedding)
    return np.array(embedding, dtype=np.float32)


def get_label_and_color(score):
    if score >= THRESHOLD_STRONG:
        return "STRONG MATCH", (0, 255, 0)
    elif score >= THRESHOLD_WEAK:
        return "PROBABLE MATCH", (0, 165, 255)
    else:
        return "UNKNOWN", (0, 0, 255)


def find_best_match(live_embedding, db_embeddings):
    best_match = None
    best_score = 0.0

    live_emb = live_embedding.reshape(1, -1)

    for person_id, name, image_path, embedding in db_embeddings:
        db_emb = parse_embedding(embedding).reshape(1, -1)
        score = cosine_similarity(live_emb, db_emb)[0][0]

        if score > best_score:
            best_score = score
            best_match = {
                "person_id": person_id,
                "name": name,
                "image_path": image_path,
                "score": round(float(score), 4)
            }

    return best_match
