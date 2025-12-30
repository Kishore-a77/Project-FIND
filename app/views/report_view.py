import streamlit as st
from app.controllers.report_controller import handle_report

def report_view():
    st.title("📌 Report Missing Person")

    with st.form("report_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        notes = st.text_area("Additional Notes")
        photo = st.file_uploader("Upload Face Photo", type=["jpg", "png", "jpeg"])

        submitted = st.form_submit_button("Submit Report")

    if submitted:
        if not name or not photo:
            st.error("Name and photo are required.")
            return

        with st.spinner("Processing..."):
            person_id = handle_report(name, age, notes, photo)

        st.success(f"Missing person reported successfully!")
        st.info(f"Person ID: {person_id}")
