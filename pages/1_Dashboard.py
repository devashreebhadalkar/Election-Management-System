
import streamlit as st
import pandas as pd

from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login
from database import get_connection


st.set_page_config(
    page_title="Election Management System | Dashboard",
    page_icon="🗳️",
    layout="wide"
)

# Apply the shared government portal design.
apply_portal_style()

# Protect the dashboard from unauthenticated access.
require_login()

# Display a consistent government-style page banner.
show_portal_banner(
    "Election Management Dashboard",
    "Overview of records and administrative activities"
)

st.write(
    "Monitor the records stored in your Election Management System database."
)

st.divider()


def get_dashboard_data():
    connection = None
    cursor = None

    try:
        connection = get_connection()

        queries = {
            "Total Voters": "SELECT COUNT(*) FROM voter",
            "Polling Booths": "SELECT COUNT(*) FROM polling_booth",
            "BLO Officers": "SELECT COUNT(*) FROM BLO",
            "Electoral Officers": "SELECT COUNT(*) FROM electoral_officer",
            "Applications": "SELECT COUNT(*) FROM application",
            "Documents": "SELECT COUNT(*) FROM document",
            "Electoral Rolls": "SELECT COUNT(*) FROM electoral_roll",
            "Claims & Objections": "SELECT COUNT(*) FROM claim_objection"
        }

        counts = {}
        cursor = connection.cursor()

        for label, query in queries.items():
            cursor.execute(query)
            counts[label] = cursor.fetchone()[0]

        return counts, None

    except Exception as error:
        return None, str(error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


counts, error = get_dashboard_data()

if error:
    st.error(f"Unable to load dashboard data: {error}")
    st.info("Please check your MySQL connection and table names.")

else:
    st.subheader("System Overview")

    row_one = st.columns(4)

    metrics_one = [
        "Total Voters",
        "Polling Booths",
        "BLO Officers",
        "Electoral Officers"
    ]

    for column, label in zip(row_one, metrics_one):
        column.metric(label, counts[label])

    row_two = st.columns(4)

    metrics_two = [
        "Applications",
        "Documents",
        "Electoral Rolls",
        "Claims & Objections"
    ]

    for column, label in zip(row_two, metrics_two):
        column.metric(label, counts[label])

    st.divider()

    st.subheader("Database Summary")

    summary = pd.DataFrame({
        "Module": list(counts.keys()),
        "Total Records": list(counts.values())
    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Counts are retrieved directly from MySQL. "
        "Records are demonstration data for an academic project."
    )

st.divider()

if st.button("🔄 Refresh Dashboard"):
    st.rerun()


# Purpose:
# Connects to MySQL and counts records in eight project tables.
# Displays record counts as dashboard metrics and a summary table.
# Requires login before showing dashboard data.
# Uses the shared government portal stylesheet for consistent styling.
