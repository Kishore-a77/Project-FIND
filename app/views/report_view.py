import streamlit as st
from app.controllers.report_controller import handle_report


def report_view():
    st.title("📌 Report Missing Person")

    with st.form("report_form"):
        # Better layout with columns
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
        
        with col2:
            age = st.number_input("Age", min_value=1, max_value=120, value=25)
        
        notes = st.text_area("Additional Notes", 
                           placeholder="Last seen location, clothing description, special features...",
                           height=100)
        
        photo = st.file_uploader("Upload Face Photo", 
                                type=["jpg", "png", "jpeg"],
                                help="Upload a clear frontal face photo for best recognition results")
        
        submitted = st.form_submit_button("Submit Report", type="primary")

    if submitted:
        if not name or name.strip() == "":
            st.error("❌ Name is required.")
            return
            
        if not photo:
            st.error("❌ Please upload a photo.")
            return
        
        # Validate photo size (optional)
        if len(photo.getvalue()) > 10 * 1024 * 1024:  # 10MB limit
            st.error("❌ Image size should be less than 10MB.")
            return

        try:
            with st.spinner("Processing image and extracting facial features..."):
                person_id = handle_report(name, age, notes, photo)
                
                # Show success message
                st.success(f"✅ **{name}** has been successfully added to the missing persons database!")
                
                # Show person details
                st.divider()
                st.subheader("Report Summary")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Person ID:** `{person_id}`")
                    st.info(f"**Name:** {name}")
                    st.info(f"**Age:** {age}")
                
                with col2:
                    # Try to display the uploaded image
                    try:
                        st.image(photo, caption="Uploaded Photo", width=200)
                    except:
                        st.write("Image preview not available")
                
                if notes and notes.strip():
                    st.info(f"**Notes:** {notes}")
                
                # Important note
                st.warning("⚠️ **Important:** Keep the Person ID for future reference. The system will now start searching for this person in live camera feeds.")

        except ValueError as e:
            st.error(f"❌ {str(e)}")
            st.info("💡 **Tips for better photos:**\n"
                   "- Use a clear frontal face photo\n"
                   "- Good lighting, no shadows on face\n"
                   "- Face should cover most of the image\n"
                   "- No sunglasses or face obstructions")
        
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            st.info("Please try again or contact support if the problem persists.")