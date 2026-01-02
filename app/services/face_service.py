import cv2
import numpy as np
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------
# Initialize InsightFace model ONCE (important)
# --------------------------------------------------
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0, det_size=(640, 640))


# --------------------------------------------------
# IMAGE COMPRESSION (Day 11 optimization)
# --------------------------------------------------
def compress_frame(frame, width=640):
    """
    Resize frame to fixed width while maintaining aspect ratio.
    This drastically improves FPS with negligible accuracy loss.
    """
    h, w, _ = frame.shape
    if w <= width:
        return frame  # No need to upscale

    ratio = width / w
    new_height = int(h * ratio)
    return cv2.resize(frame, (width, new_height))


# --------------------------------------------------
# IMAGE-BASED EMBEDDING (Day 4 flow)
# --------------------------------------------------
def get_face_embedding(image_path: str):
    """
    Detects the largest face in an image and returns its embedding.
    """

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("❌ Image not found or invalid path")

    faces = face_app.get(img)

    if not faces:
        raise ValueError("❌ No face detected in the image")

    face = max(
        faces,
        key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
    )

    embedding = face.embedding

    if embedding is None:
        raise ValueError("❌ Failed to extract face embedding")

    return embedding


# --------------------------------------------------
# LIVE VIDEO FACE DETECTION (with compression)
# --------------------------------------------------
def detect_faces(frame):
    """
    Detect faces from a video frame (with compression).
    """
    frame = compress_frame(frame)
    return face_app.get(frame)


# --------------------------------------------------
# EMBEDDING COMPARISON
# --------------------------------------------------
def compare_faces(emb1: np.ndarray, emb2: np.ndarray):
    """
    Compares two face embeddings using cosine similarity.
    """

    emb1 = emb1 / np.linalg.norm(emb1)
    emb2 = emb2 / np.linalg.norm(emb2)

    score = cosine_similarity(
        emb1.reshape(1, -1),
        emb2.reshape(1, -1)
    )[0][0]

    return round(float(score), 4)
