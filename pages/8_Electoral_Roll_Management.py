
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Electoral Roll Management",
    page_icon="📚",
    layout="wide"
)

apply_portal_style()

# Require login before accessing electoral roll records.
require_login()

show_portal_banner(
    "Electoral Roll Management",
    "Manage and maintain electoral roll records"
)

st.caption("Academic project demonstration using fictional demo records.")

st.divider()


def run_query(query, values=None, fetch=False):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, values or ())

        if fetch:
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return pd.DataFrame(rows, columns=columns)

        connection.commit()
        return True

    except mysql.connector.Error as error:
        if connection and connection.is_connected():
            connection.rollback()

        st.error(f"Database error: {error}")
        return None

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


roll_types = [
    "Draft Roll",
    "Final Roll",
    "Supplementary Roll",
    "Other"
]

roll_statuses = [
    "Draft",
    "Under Review",
    "Published",
    "Archived"
]


tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Roll",
    "📋 View / Search",
    "✏️ Update Roll",
    "🗑️ Delete Roll"
])


# ADD ELECTORAL ROLL
with tab1:
    st.subheader("Add an Electoral Roll Record")
    st.write("Enter the details for a new demo electoral roll.")

    with st.form("add_roll_form"):
        roll_type = st.selectbox("Roll Type", roll_types)
        publish_date = st.date_input("Publish Date")
        status = st.selectbox("Status", roll_statuses)

        submitted = st.form_submit_button(
            "Add Electoral Roll",
            use_container_width=True
        )

        if submitted:
            result = run_query(
                """
                INSERT INTO electoral_roll
                    (Roll_Type, Publish_Date, Status)
                VALUES (%s, %s, %s)
                """,
                (roll_type, publish_date, status)
            )

            if result:
                st.success("Electoral roll record added successfully!")
                st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Electoral Rolls")

    search_text = st.text_input(
        "Search by Roll ID, Roll Type, or Status",
        placeholder="Enter an ID, roll type, or status..."
    )

    rolls = run_query(
        """
        SELECT Roll_ID, Roll_Type, Publish_Date, Status
        FROM electoral_roll
        WHERE CAST(Roll_ID AS CHAR) LIKE %s
           OR Roll_Type LIKE %s
           OR Status LIKE %s
        ORDER BY Roll_ID DESC
        """,
        tuple([f"%{search_text}%"] * 3),
        fetch=True
    )

    if rolls is not None:
        st.dataframe(
            rolls,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Records found: {len(rolls)}")


# UPDATE ELECTORAL ROLL
with tab3:
    st.subheader("Update Electoral Roll Details")

    rolls = run_query(
        """
        SELECT Roll_ID, Roll_Type, Publish_Date, Status
        FROM electoral_roll
        ORDER BY Roll_ID
        """,
        fetch=True
    )

    if rolls is not None and not rolls.empty:
        roll_ids = rolls["Roll_ID"].tolist()

        selected_id = st.selectbox(
            "Select Roll ID",
            roll_ids,
            key="update_roll_id"
        )

        selected = rolls[rolls["Roll_ID"] == selected_id].iloc[0]

        current_type = selected["Roll_Type"]
        type_index = (
            roll_types.index(current_type)
            if current_type in roll_types
            else 0
        )

        current_status = selected["Status"]
        status_index = (
            roll_statuses.index(current_status)
            if current_status in roll_statuses
            else 0
        )

        with st.form("update_roll_form"):
            new_type = st.selectbox(
                "Roll Type",
                roll_types,
                index=type_index
            )

            current_date = selected["Publish_Date"]

            if pd.isna(current_date):
                current_date = pd.Timestamp.today().date()
            elif hasattr(current_date, "date"):
                current_date = current_date.date()

            new_date = st.date_input(
                "Publish Date",
                value=current_date
            )

            new_status = st.selectbox(
                "Status",
                roll_statuses,
                index=status_index
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                result = run_query(
                    """
                    UPDATE electoral_roll
                    SET Roll_Type = %s,
                        Publish_Date = %s,
                        Status = %s
                    WHERE Roll_ID = %s
                    """,
                    (new_type, new_date, new_status, selected_id)
                )

                if result:
                    st.success("Electoral roll updated successfully!")
                    st.rerun()

    else:
        st.info("No electoral roll records are available.")


# DELETE ELECTORAL ROLL
with tab4:
    st.subheader("Delete an Electoral Roll Record")

    rolls = run_query(
        """
        SELECT Roll_ID, Roll_Type, Publish_Date, Status
        FROM electoral_roll
        ORDER BY Roll_ID
        """,
        fetch=True
    )

    if rolls is not None and not rolls.empty:
        roll_ids = rolls["Roll_ID"].tolist()

        delete_id = st.selectbox(
            "Select Roll ID to delete",
            roll_ids,
            key="delete_roll_id"
        )

        st.warning(
            f"You selected electoral roll record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Electoral Roll", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM electoral_roll WHERE Roll_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Electoral roll record deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    else:
        st.info("No electoral roll records are available.")
