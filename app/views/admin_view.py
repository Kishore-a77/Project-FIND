import streamlit as st
from datetime import datetime

from app.services.db_service import (
    fetch_all_missing_persons,
    fetch_all_match_logs,
    delete_missing_person,
    get_statistics
)


def admin_view():
    st.title("🛠️ Admin Panel")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard", 
        "👥 Missing Persons", 
        "📋 Match History"
    ])
    
    with tab1:
        st.subheader("System Dashboard")
        
        # Get statistics
        stats = get_statistics()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Missing Persons", stats["total_persons"])
        
        with col2:
            st.metric("Total Matches", stats["total_matches"])
            
        with col3:
            st.metric("Confirmed Matches", stats["confirmed_matches"])
            
        with col4:
            st.metric("Pending Matches", stats["pending_matches"])
        
        st.divider()
        
        # Quick actions
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Database", use_container_width=True):
                st.rerun()
                
        with col2:
            if st.button("🗑️ Clear Old Logs", use_container_width=True):
                st.warning("This feature is not implemented yet")
    
    with tab2:
        st.subheader("Missing Persons Database")
        
        # Fetch all missing persons
        persons = fetch_all_missing_persons()
        
        if not persons:
            st.info("No missing persons in database.")
        else:
            for person in persons:
                person_id, name, age, notes, image_path, created_at = person
                
                with st.expander(f"👤 {name} (ID: {person_id})"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if image_path:
                            try:
                                st.image(image_path, caption=name, width=150)
                            except:
                                st.warning("Image not found")
                    
                    with col2:
                        st.write(f"**Age:** {age if age else 'Not specified'}")
                        st.write(f"**Notes:** {notes if notes else 'No notes'}")
                        st.write(f"**Added on:** {created_at}")
                        
                        # Delete button
                        if st.button(f"Delete {name}", key=f"del_{person_id}"):
                            if delete_missing_person(person_id):
                                st.success(f"Deleted {name}")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete {name}")
    
    with tab3:
        st.subheader("Match History")
        
        # Fetch all match logs
        logs = fetch_all_match_logs()
        
        if not logs:
            st.info("No match logs found.")
        else:
            # Create a table view
            for log in logs:
                (log_id, person_id, confidence, camera_location, 
                 match_time, alert_sent, operator_decision, escalation_level) = log
                
                # Determine color based on decision
                if operator_decision == "CONFIRMED":
                    color = "🟢"
                    badge = "✅ CONFIRMED"
                elif operator_decision == "REJECTED":
                    color = "🔴"
                    badge = "❌ REJECTED"
                else:
                    color = "🟡"
                    badge = "⏳ PENDING"
                
                with st.expander(f"{color} Match: {person_id} at {match_time}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Person ID:** {person_id}")
                        st.write(f"**Camera:** {camera_location}")
                        st.write(f"**Time:** {match_time}")
                        
                    with col2:
                        st.write(f"**Confidence:** {confidence:.3f}")
                        st.write(f"**Decision:** {badge}")
                        st.write(f"**Alert Sent:** {'✅' if alert_sent else '❌'}")
                        st.write(f"**Escalation:** Level {escalation_level}")
                    
                    st.write(f"**Log ID:** `{log_id}`")