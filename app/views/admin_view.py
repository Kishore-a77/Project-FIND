import streamlit as st
import pandas as pd
from app.controllers.admin_controller import (
    get_missing_persons,
    get_match_logs,
    remove_person
)
from app.views.ui_utils import confidence_badge


def admin_view():
    st.title("🛂 Admin Control Panel")

    tab1, tab2 = st.tabs(["Missing Persons", "Match Logs"])

    # -------------------------------
    # TAB 1: Missing Persons
    # -------------------------------
    with tab1:
        st.subheader("Registered Missing Persons")

        persons = get_missing_persons()

        if not persons:
            st.info("No missing persons found.")
        else:
            df = pd.DataFrame(
                persons,
                columns=["Person ID", "Name", "Age", "Notes", "Image Path", "Created At"]
            )
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.subheader("Remove Person")

            person_id = st.text_input("Enter Person ID")
            confirm = st.checkbox("I understand this will permanently delete the record")

            if st.button("Delete Person"):
                if not person_id:
                    st.error("Person ID required")
                elif not confirm:
                    st.warning("Please confirm deletion")
                else:
                    remove_person(person_id)
                    st.success("Person removed successfully")

    # -------------------------------
    # TAB 2: Match Logs
    # -------------------------------
    with tab2:
        st.subheader("Match Audit Logs")

        logs = get_match_logs()

        if not logs:
            st.info("No match logs available.")
            return

        df_logs = pd.DataFrame(
            logs,
            columns=[
                "Log ID",
                "Person ID",
                "Confidence",
                "Camera",
                "Match Time",
                "Decision",
                "Alert Sent",
            ]
        )

        st.dataframe(df_logs, use_container_width=True)

        st.divider()
        st.subheader("Visual Confidence Breakdown")

        for _, row in df_logs.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 3])

                with col1:
                    st.text(row["Person ID"])

                with col2:
                    st.text(f"{row['Confidence']:.3f}")

                with col3:
                    confidence_badge(
                        row["Confidence"],
                        decision=row["Decision"]
                    )

                with col4:
                    st.text(row["Camera"])

                st.divider()

        st.markdown("### 📊 Quick Stats")
        st.metric("Total Matches", len(df_logs))
        st.metric("Confirmed", len(df_logs[df_logs["Decision"] == "CONFIRMED"]))
        st.metric("Rejected", len(df_logs[df_logs["Decision"] == "REJECTED"]))
