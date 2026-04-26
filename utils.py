import streamlit as st
import requests

def send_feedback_formspree(name, email, message, formspree_endpoint):
    try:
        response = requests.post(
            formspree_endpoint,
            data={"name": name, "email": email, "message": message},
            headers={"Accept": "application/json"}
        )
        if response.status_code == 200:
            return True, "Feedback sent successfully!"
        else:
            return False, "Error sending feedback. Please try again."
    except Exception as e:
        return False, f"Error: {str(e)}"

def show_feedback_form():
    with st.sidebar:
        st.markdown("---")
        st.subheader("📝 Feedback")
        formspree_endpoint = st.secrets.get("FORMSPREE_ENDPOINT")

        if formspree_endpoint:
            with st.form("feedback_form"):
                feedback_name = st.text_input("Your name", placeholder="John Doe")
                feedback_email = st.text_input("Your email", placeholder="you@example.com")
                feedback_message = st.text_area("Your feedback", placeholder="Tell us what you think...", height=100)
                submit_feedback = st.form_submit_button("Send Feedback", use_container_width=True)

                if submit_feedback:
                    if feedback_name and feedback_email and feedback_message:
                        success, message = send_feedback_formspree(feedback_name, feedback_email, feedback_message, formspree_endpoint)
                        if success:
                            st.success(message)
                        else:
                            st.warning(message)
                    else:
                        st.error("Please fill in all fields")
        else:
            st.info("ℹ️ Feedback form not configured yet")
