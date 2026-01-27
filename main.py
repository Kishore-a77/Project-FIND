import sys
from pathlib import Path
import time

# Ensure project root in path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.views.report_view import report_view
from app.views.monitor_view import monitor_view
from app.views.admin_view import admin_view

st.set_page_config(
    page_title="Project FIND",
    layout="wide",
    page_icon="🔍"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .status-running {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .status-stopped {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔍 Project FIND")
st.sidebar.markdown("---")

# Add system status in sidebar
st.sidebar.subheader("System Status")
if 'camera_status' not in st.session_state:
    st.session_state.camera_status = "Stopped"

status_color = "🟢" if st.session_state.camera_status == "Running" else "🔴"
st.sidebar.markdown(f"{status_color} **Camera:** {st.session_state.camera_status}")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "📝 Report Missing Person",
        "🎥 Live Monitoring",
        "🛠️ Admin Panel"
    ]
)

if page == "📝 Report Missing Person":
    report_view()

elif page == "🎥 Live Monitoring":
    monitor_view()

elif page == "🛠️ Admin Panel":
    admin_view()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "**Project FIND** - Face Identification & Detection System\n\n"
    "Version 1.0.0\n"
    "Real-time missing person detection"
)