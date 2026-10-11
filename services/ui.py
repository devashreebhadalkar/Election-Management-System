
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STYLESHEET_PATH = PROJECT_ROOT / "css" / "style.css"


def apply_portal_style():
    """Apply the shared government-portal design to a Streamlit page."""

    if not STYLESHEET_PATH.exists():
        st.warning(
            "Portal stylesheet not found. "
            f"Expected file: {STYLESHEET_PATH}"
        )
        return

    css = STYLESHEET_PATH.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def show_portal_banner(title, subtitle=""):
    """Display a consistent title banner on a management page."""

    safe_title = (
        str(title)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    safe_subtitle = (
        str(subtitle)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    st.markdown(
        f"""
        <div class="portal-banner">
            <h3>{safe_title}</h3>
            <div>{safe_subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
