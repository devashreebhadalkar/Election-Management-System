
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Electoral Officer Management | Election Management System",
    page_icon="👮",
    layout="wide"
)

apply_portal_style()

# Require login before accessing officer records.
require_login()

show_portal_banner(
    "Electoral Officer Management",
    "Manage and maintain demonstration officer records"
)

st.write(
    "View, search, add, update and delete electoral officer records."
)

st.info(
    "Use fictional demo records for academic testing."
)

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


designations = [
    "Electoral Officer",
    "Returning Officer",
    "Assistant Electoral Officer",
    "Other"
]

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Officer",
    "📋 View / Search",
    "✏️ Update Officer",
    "🗑️ Delete Officer"
])


# ADD OFFICER
with tab1:
    st.subheader("Add an Electoral Officer")

    with st.form("add_officer_form"):
        name = st.text_input("Officer Name")

        designation = st.selectbox(
            "Designation",
            designations
        )

        office_name = st.text_input("Office Name")

        submitted = st.form_submit_button(
            "Add Officer",
            use_container_width=True
        )

        if submitted:
            if not name.strip() or not office_name.strip():
                st.error("Please enter the officer name and office name.")
            else:
                result = run_query(
                    """
                    INSERT INTO electoral_officer
                        (Name, Designation, Office_Name)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        name.strip(),
                        designation,
                        office_name.strip()
                    )
                )

                if result:
                    st.success("Officer record added successfully!")
                    st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Officers")

    search_text = st.text_input(
        "Search by Officer ID, Name, Designation, or Office",
        placeholder="Enter an ID, designation, or office name..."
    )

    officers = run_query(
        """
        SELECT Officer_ID, Name, Designation, Office_Name
        FROM electoral_officer
        WHERE CAST(Officer_ID AS CHAR) LIKE %s
           OR Name LIKE %s
           OR Designation LIKE %s
           OR Office_Name LIKE %s
        ORDER BY Officer_ID DESC
        """,
        tuple([f"%{search_text}%"] * 4),
        fetch=True
    )

    if officers is not None:
        st.dataframe(
            officers,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Records found: {len(officers)}")


# UPDATE OFFICER
with tab3:
    st.subheader("Update Officer Details")

    officers = run_query(
        """
        SELECT Officer_ID, Name, Designation, Office_Name
        FROM electoral_officer
        ORDER BY Officer_ID
        """,
        fetch=True
    )

    if officers is not None and not officers.empty:
        officer_ids = officers["Officer_ID"].tolist()

        selected_id = st.selectbox(
            "Select Officer ID",
            officer_ids,
            key="update_officer_id"
        )

        selected = officers[
            officers["Officer_ID"] == selected_id
        ].iloc[0]

        current_designation = selected["Designation"]

        designation_index = (
            designations.index(current_designation)
            if current_designation in designations
            else 0
        )

        with st.form("update_officer_form"):
            new_name = st.text_input(
                "Officer Name",
                value=str(selected["Name"])
            )

            new_designation = st.selectbox(
                "Designation",
                designations,
                index=designation_index
            )

            new_office = st.text_input(
                "Office Name",
                value=str(selected["Office_Name"])
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                if not new_name.strip() or not new_office.strip():
                    st.error("Please fill in the required fields.")
                else:
                    result = run_query(
                        """
                        UPDATE electoral_officer
                        SET Name = %s,
                            Designation = %s,
                            Office_Name = %s
                        WHERE Officer_ID = %s
                        """,
                        (
                            new_name.strip(),
                            new_designation,
                            new_office.strip(),
                            selected_id
                        )
                    )

                    if result:
                        st.success("Officer record updated successfully!")
                        st.rerun()

    elif officers is not None:
        st.info("No officer records are available.")


# DELETE OFFICER
with tab4:
    st.subheader("Delete an Officer Record")

    officers = run_query(
        """
        SELECT Officer_ID, Name, Designation, Office_Name
        FROM electoral_officer
        ORDER BY Officer_ID
        """,
        fetch=True
    )

    if officers is not None and not officers.empty:
        officer_ids = officers["Officer_ID"].tolist()

        delete_id = st.selectbox(
            "Select Officer ID to delete",
            officer_ids,
            key="delete_officer_id"
        )

        st.warning(
            f"You selected officer record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Officer", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM electoral_officer WHERE Officer_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Officer record deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    elif officers is not None:
        st.info("No officer records are available.")


# Purpose:
# Manages electoral officer records using MySQL CRUD operations.
# Requires login before accessing officer records.
# Uses fictional demonstration data for academic testing.
