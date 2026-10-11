
import streamlit as st


def require_login():
    """Prevent access to a page when the user is not logged in."""

    if not st.session_state.get("authenticated", False):
        st.warning("Please sign in to access this page.")
        st.info(
            "Return to the main Election Management System page "
            "and log in with your demo credentials."
        )
        st.stop()
