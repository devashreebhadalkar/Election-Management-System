
import streamlit as st
from services.ui import apply_portal_style

st.set_page_config(
    page_title="Election Management System",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_portal_style()

# Demo credentials for local academic testing only.
# Change these before sharing the project.
DEMO_USERS = {
    "admin": {
        "password": "Admin@123",
        "role": "Admin"
    },
    "officer": {
        "password": "Officer@123",
        "role": "Electoral Officer"
    },
    "blo": {
        "password": "BLO@123",
        "role": "BLO"
    },
    "voter": {
        "password": "Voter@123",
        "role": "Voter"
    }
}

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fc;
}
.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}
.login-title {
    color: #14284b;
    font-size: 30px;
    font-weight: 750;
    text-align: center;
}
.login-subtitle {
    color: #64748b;
    font-size: 15px;
    text-align: center;
}
div.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    min-height: 44px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


def logout():
    st.session_state["authenticated"] = False
    st.session_state.pop("username", None)
    st.session_state.pop("role", None)


if not st.session_state.get("authenticated", False):
    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.write("")
        st.markdown(
            '<div style="text-align:center;font-size:54px;">🗳️</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="login-title">Election Management System</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="login-subtitle">'
            'Manage voter records, applications and electoral information'
            '</div>',
            unsafe_allow_html=True
        )

        st.write("")

        with st.container(border=True):
            st.subheader("Welcome back")
            st.caption("Sign in to access your workspace")

            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                ).strip().lower()

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                role = st.selectbox(
                    "Login as",
                    ["Admin", "Electoral Officer", "BLO", "Voter"]
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )

            if submitted:
                user = DEMO_USERS.get(username)

                if (
                    user
                    and user["password"] == password
                    and user["role"] == role
                ):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.rerun()
                else:
                    st.error(
                        "Invalid username, password, or selected role."
                    )

        with st.expander("View demo login credentials"):
            st.warning(
                "These credentials are visible for academic testing only. "
                "Do not use them for real accounts."
            )
            st.code(
                "Admin: admin / Admin@123\n"
                "Electoral Officer: officer / Officer@123\n"
                "BLO: blo / BLO@123\n"
                "Voter: voter / Voter@123"
            )

        st.caption("Academic project • Demo environment")

else:
    st.sidebar.title("🗳️ Election Management System")
    st.sidebar.write(f"Signed in as: **{st.session_state['username']}**")
    st.sidebar.write(f"Role: **{st.session_state['role']}**")

    if st.sidebar.button("Sign out", use_container_width=True):
        logout()
        st.rerun()

    st.title("Welcome to the Election Management System")
    st.success("Demo login successful!")
    st.write(
        "Use the page navigation in the sidebar to open your dashboard "
        "and management modules."
    )
    st.info(
        "This demo login is not secure authentication. "
        "Role-based access restrictions have not yet been implemented."
    )
