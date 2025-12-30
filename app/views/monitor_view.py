import streamlit as st
import cv2
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from streamlit_autorefresh import st_autorefresh

from app.services.face_service import face_app
from app.services.matching_service import find_best_match
from app.services.snowflake_service import fetch_all_persons_with_images
from app.views.ui_utils import confidence_badge

CAMERA_LOCATION = "Main Gate Camera"


# -------------------------------------------------
# Cache DB embeddings
# -------------------------------------------------
@st.cache_data
def load_db_embeddings():
    return fetch_all_persons_with_images()


# -------------------------------------------------
# Video Processor
# -------------------------------------------------
class FaceProcessor(VideoProcessorBase):
    def __init__(self):
        self.db_embeddings = load_db_embeddings()
        self.latest_match = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        faces = face_app.get(img)
        self.latest_match = None

        for face in faces:
            emb = face.embedding
            match = find_best_match(emb, self.db_embeddings)

            x1, y1, x2, y2 = face.bbox.astype(int)

            if match and match["score"] >= 0.65:
                label_type = "STRONG" if match["score"] >= 0.80 else "PROBABLE"
                label = f"{match['name']} | {label_type} ({match['score']:.3f})"
                color = (0, 255, 0) if match["score"] >= 0.80 else (0, 165, 255)

                self.latest_match = {
                    "person_id": match["person_id"],
                    "name": match["name"],
                    "score": match["score"],
                    "camera_location": CAMERA_LOCATION,
                }
            else:
                label = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                img,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# -------------------------------------------------
# Streamlit View
# -------------------------------------------------
def monitor_view():
    st.title("🎥 Live Monitoring (WebRTC)")
    st.caption("Industry-grade webcam stream using streamlit-webrtc")

    st_autorefresh(interval=700, key="monitor-refresh")

    webrtc_ctx = webrtc_streamer(
        key="face-monitor",
        video_processor_factory=FaceProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    st.divider()
    st.subheader("Manual Verification")

    if "operator_action" not in st.session_state:
        st.session_state.operator_action = None

    if webrtc_ctx.video_processor and webrtc_ctx.video_processor.latest_match:
        match = webrtc_ctx.video_processor.latest_match

        st.success("AI Match Detected")
        st.write(f"**Name:** {match['name']}")
        st.write(f"**Confidence:** {match['score']:.3f}")
        confidence_badge(match["score"])
        st.write(f"**Camera:** {match['camera_location']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Match"):
                st.session_state.operator_action = "CONFIRMED"

        with col2:
            if st.button("❌ Reject Match"):
                st.session_state.operator_action = "REJECTED"

    else:
        st.info("Waiting for a confirmed AI match…")

    if st.session_state.operator_action == "CONFIRMED":
        st.success("✅ Match CONFIRMED. Alert triggered and logged.")
    elif st.session_state.operator_action == "REJECTED":
        st.warning("❌ Match REJECTED. No alert sent.")
