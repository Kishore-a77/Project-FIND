import streamlit as st
import requests
from datetime import datetime
import time
import os

from app.services.db_service import (
    fetch_pending_matches,
    update_match_decision
)
from app.views.ui_utils import confidence_badge
from app.controllers.camera_controller import CameraController

# Initialize session state
if 'camera_controller' not in st.session_state:
    st.session_state.camera_controller = CameraController()

if 'camera_instructions' not in st.session_state:
    st.session_state.camera_instructions = ""
    
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/confirmed-match"

def trigger_n8n_alert(match):
    payload = {
        "person_id": match["person_id"],
        "confidence": match["confidence"],
        "camera_location": match["camera_location"],
        "match_time": str(datetime.utcnow()),
        "escalation_level": 2,
        "acknowledged": False,
    }
    try:
        return requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5).status_code == 200
    except Exception:
        return False


def monitor_view():
    st.title("🛂 Live Monitoring – Control Room")
    
    # Camera Control Section
    st.subheader("🎥 Camera Control")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        start_button = st.button("▶️ Start Camera", type="primary", use_container_width=True, 
                               help="Open camera in a separate window")
        
    with col2:
        stop_button = st.button("⏹️ Stop Camera", type="secondary", use_container_width=True,
                              help="Close the camera window")
    
    with col3:
        status = st.session_state.camera_controller.get_status()
        if status == "Running":
            st.markdown(
                "<div style='background-color: #4CAF50; color: white; padding: 10px; "
                "border-radius: 5px; text-align: center;'>"
                "🟢 Camera Status: RUNNING</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='background-color: #f44336; color: white; padding: 10px; "
                "border-radius: 5px; text-align: center;'>"
                "🔴 Camera Status: STOPPED</div>",
                unsafe_allow_html=True
            )
    
    # Handle button clicks
    if start_button:
        success, message = st.session_state.camera_controller.start_camera()
        st.session_state.camera_instructions = message
        st.session_state.show_instructions = True
        st.rerun()
    
    if stop_button:
        success, message = st.session_state.camera_controller.stop_camera()
        st.session_state.camera_instructions = message
        st.session_state.show_instructions = True
        st.rerun()
    
    # Show instructions if available
    if st.session_state.show_instructions and st.session_state.camera_instructions:
        st.markdown("---")
        st.subheader("📋 Instructions")
        
        # Display the instructions
        lines = st.session_state.camera_instructions.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith("✅") or line.startswith("❌"):
                    if "error" in line.lower() or "failed" in line.lower():
                        st.error(line)
                    else:
                        st.success(line)
                elif line.startswith("cd ") or line.startswith("python"):
                    st.code(line, language="bash")
                else:
                    st.write(line)
        
        # Add a close button for the instructions
        if st.button("Got it!", key="close_instructions"):
            st.session_state.show_instructions = False
            st.rerun()
    
    st.markdown("---")
    
    # Camera Feed Information
    st.subheader("📹 Live Camera Feed Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.info("""
        **How to Start Camera:**
        1. Click "Start Camera" button above
        2. Follow the instructions to open camera
        3. A separate window will open with live feed
        4. Face detections will appear with colored boxes
        """)
    
    with info_col2:
        st.info("""
        **Color Legend:**
        - 🟢 **Green Box**: Strong match (≥ 0.80 confidence)
        - 🟡 **Yellow Box**: Probable match (0.65-0.80 confidence)
        - 🔴 **Red Box**: Unknown person (no match or low confidence)
        
        **To Stop**: Close the camera window or press 'q'
        """)
    
    st.markdown("---")
    
    # Pending Matches Section
    st.subheader("🔍 Pending Matches")
    
    # Auto-refresh every 10 seconds if camera is running
    if st.session_state.camera_controller.is_running:
        refresh_container = st.empty()
        with refresh_container:
            st.markdown("🔄 *Auto-refreshing every 10 seconds*")
        
        # Simple auto-refresh
        time.sleep(10)
        st.rerun()
    
    matches = fetch_pending_matches()
    
    if not matches:
        st.info("No pending matches found.")
    else:
        for log in matches:
            log_id, person_id, confidence, camera, match_time = log

            with st.container():
                st.markdown(f"### 👤 Match Detected")
                
                # Display match info in columns
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Person ID:** `{person_id}`")
                    st.write(f"**Camera Location:** {camera}")
                    st.write(f"**Detection Time:** {match_time}")
                
                with col_info2:
                    st.write(f"**Confidence Score:** {confidence:.3f}")
                    confidence_badge(confidence)
                
                # Decision buttons
                st.markdown("#### Action Required:")
                col_btn1, col_btn2, col_space = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button(f"✅ Confirm Match", key=f"confirm_{log_id}", 
                               use_container_width=True, type="primary"):
                        alert_sent = trigger_n8n_alert({
                            "person_id": person_id,
                            "confidence": confidence,
                            "camera_location": camera,
                        })

                        update_match_decision(
                            log_id=log_id,
                            decision="CONFIRMED",
                            alert_sent=alert_sent,
                            escalation_level=2
                        )
                        st.success("✅ Match confirmed and alert sent!")
                        time.sleep(1)
                        st.rerun()

                with col_btn2:
                    if st.button(f"❌ Reject Match", key=f"reject_{log_id}", 
                               use_container_width=True):
                        update_match_decision(
                            log_id=log_id,
                            decision="REJECTED",
                            alert_sent=False,
                            escalation_level=0
                        )
                        st.warning("❌ Match rejected")
                        time.sleep(1)
                        st.rerun()
                
                st.markdown("---")