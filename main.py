import sys
from pathlib import Path

# Ensure project root in path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.views.report_view import report_view
from app.views.monitor_view import monitor_view
from app.views.admin_view import admin_view

st.set_page_config(
    page_title="Project FIND",
    layout="wide"
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Report Missing Person",
        "Live Monitoring",
        "Admin Panel"
    ]
)

if page == "Report Missing Person":
    report_view()

elif page == "Live Monitoring":
    monitor_view()

elif page == "Admin Panel":
    admin_view()
