import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.snowflake_service import fetch_analytics_data

def analytics_view():
    st.title("📊 Analytics Dashboard")

    data = fetch_analytics_data()
    if not data:
        st.info("No analytics data available yet.")
        return

    df = pd.DataFrame(
        data,
        columns=[
            "Decision",
            "Confidence",
            "Camera",
            "Escalation Level",
            "Time"
        ]
    )

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", len(df))
    col2.metric("Confirmed", len(df[df["Decision"] == "CONFIRMED"]))
    col3.metric("Rejected", len(df[df["Decision"] == "REJECTED"]))

    st.divider()

    # Confidence distribution
    st.subheader("Confidence Distribution")
    fig1 = px.histogram(df, x="Confidence", nbins=20)
    st.plotly_chart(fig1, use_container_width=True)

    # Camera activity
    st.subheader("Camera-wise Activity")
    fig2 = px.bar(df, x="Camera", color="Decision")
    st.plotly_chart(fig2, use_container_width=True)

    # Escalation stats
    st.subheader("Escalation Levels")
    fig3 = px.pie(df, names="Escalation Level")
    st.plotly_chart(fig3, use_container_width=True)
