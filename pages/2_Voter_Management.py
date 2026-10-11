
import streamlit as st
import pandas as pd
import mysql.connector

from datetime import date
from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Voter Management | Election Management System",
    page_icon="🗳️",
    layout="wide"
)

apply_portal_style()

# Protect this page: users must sign in first.
require_login()

show_portal_banner(
    "Voter Management",
    "Manage, search, update and review demonstration voter records"
)

st.write(
    "Use the tabs below to maintain fictional voter records "
    "for your academic project."
)

st.divider()


def fetch_voters(search=""):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if search.strip():
            term = f"%{search.strip()}%"
            cursor.execute(
                """
                SELECT Voter_ID, EPIC_Number, Name, Date_of_Birth,
                       Gender, Address, Mobile_Number_Authenticated,
                       Aadhaar_Number, Verification_Status
                FROM voter
                WHERE CAST(Voter_ID AS CHAR) LIKE %s
                   OR Name LIKE %s
                   OR EPIC_Number LIKE %s
                ORDER BY Voter_ID
                """,
                (term, term, term)
            )
        else:
            cursor.execute(
                """
                SELECT Voter_ID, EPIC_Number, Name, Date_of_Birth,
                       Gender, Address, Mobile_Number_Authenticated,
                       Aadhaar_Number, Verification_Status
                FROM voter
                ORDER BY Voter_ID
                """
            )

        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def execute_query(query, values):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        return True, "Database updated successfully."

    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        return False, str(error)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def valid_voter(epic, name):
    if not name.strip():
        st.error("Please enter the voter's name.")
        return False

    if not epic.strip():
        st.error("Please enter an EPIC number.")
        return False

    return True


tab_add, tab_view, tab_update, tab_delete = st.tabs(
    [
        "➕ Add Voter",
        "📋 View & Search",
        "✏️ Update Voter",
        "🗑️ Delete Voter"
    ]
)


with tab_add:
    st.subheader("Add a Voter Record")

    with st.form("add_voter_form", clear_on_submit=True):
        epic = st.text_input("EPIC Number")
        name = st.text_input("Full Name")

        dob = st.date_input(
            "Date of Birth",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )

        gender = st.selectbox(
            "Gender",
            ["Not specified", "Female", "Male", "Other"]
        )

        address = st.text_area("Address")
        mobile = st.text_input("Authenticated Mobile Number (demo only)")
        aadhaar = st.text_input("Aadhaar Placeholder (demo only)")

        status = st.selectbox(
            "Verification Status",
            ["Pending", "Verified", "Rejected"]
        )

        submitted = st.form_submit_button(
            "Add Voter",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if valid_voter(epic, name):
                query = """
                    INSERT INTO voter
                    (EPIC_Number, Name, Date_of_Birth, Gender, Address,
                     Mobile_Number_Authenticated, Aadhaar_Number,
                     Verification_Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    epic.strip(),
                    name.strip(),
                    dob,
                    None if gender == "Not specified" else gender,
                    address.strip() or None,
                    mobile.strip() or None,
                    aadhaar.strip() or None,
                    status
                )

                success, message = execute_query(query, values)

                if success:
                    st.success("Voter record added successfully!")
                else:
                    st.error(f"Could not add voter: {message}")


with tab_view:
    st.subheader("View and Search Voters")

    search = st.text_input(
        "Search by Voter ID, name, or EPIC number",
        key="voter_search"
    )

    try:
        records = fetch_voters(search)

        if records:
            df = pd.DataFrame(records)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.caption(f"Records found: {len(records)}")
        else:
            st.info("No matching voter records found.")

    except mysql.connector.Error as error:
        st.error(f"Could not load voter records: {error}")


with tab_update:
    st.subheader("Update a Voter Record")

    try:
        all_voters = fetch_voters()

        if not all_voters:
            st.info("Add a voter record before trying to update one.")
        else:
            voter_options = {
                f"{v['Voter_ID']} — {v['Name']} "
                f"({v['EPIC_Number'] or 'No EPIC'})": v["Voter_ID"]
                for v in all_voters
            }

            selected_label = st.selectbox(
                "Select voter",
                list(voter_options.keys()),
                key="update_voter_selection"
            )

            selected_id = voter_options[selected_label]

            selected_voter = next(
                v for v in all_voters
                if v["Voter_ID"] == selected_id
            )

            current_dob = (
                selected_voter["Date_of_Birth"] or date(2000, 1, 1)
            )

            if hasattr(current_dob, "date"):
                current_dob = current_dob.date()

            current_gender = selected_voter["Gender"] or "Not specified"

            gender_options = [
                "Not specified", "Female", "Male", "Other"
            ]

            if current_gender not in gender_options:
                current_gender = "Not specified"

            current_status = (
                selected_voter["Verification_Status"] or "Pending"
            )

            status_options = ["Pending", "Verified", "Rejected"]

            if current_status not in status_options:
                current_status = "Pending"

            with st.form("update_voter_form"):
                updated_epic = st.text_input(
                    "EPIC Number",
                    value=selected_voter["EPIC_Number"] or ""
                )

                updated_name = st.text_input(
                    "Full Name",
                    value=selected_voter["Name"] or ""
                )

                updated_dob = st.date_input(
                    "Date of Birth",
                    value=current_dob,
                    min_value=date(1900, 1, 1),
                    max_value=date.today()
                )

                updated_gender = st.selectbox(
                    "Gender",
                    gender_options,
                    index=gender_options.index(current_gender)
                )

                updated_address = st.text_area(
                    "Address",
                    value=selected_voter["Address"] or ""
                )

                updated_mobile = st.text_input(
                    "Authenticated Mobile Number (demo only)",
                    value=selected_voter[
                        "Mobile_Number_Authenticated"
                    ] or ""
                )

                updated_aadhaar = st.text_input(
                    "Aadhaar Placeholder (demo only)",
                    value=selected_voter["Aadhaar_Number"] or ""
                )

                updated_status = st.selectbox(
                    "Verification Status",
                    status_options,
                    index=status_options.index(current_status)
                )

                update_submitted = st.form_submit_button(
                    "Save Changes",
                    type="primary",
                    use_container_width=True
                )

                if update_submitted:
                    if valid_voter(updated_epic, updated_name):
                        query = """
                            UPDATE voter
                            SET EPIC_Number = %s,
                                Name = %s,
                                Date_of_Birth = %s,
                                Gender = %s,
                                Address = %s,
                                Mobile_Number_Authenticated = %s,
                                Aadhaar_Number = %s,
                                Verification_Status = %s
                            WHERE Voter_ID = %s
                        """

                        values = (
                            updated_epic.strip(),
                            updated_name.strip(),
                            updated_dob,
                            None if updated_gender == "Not specified"
                            else updated_gender,
                            updated_address.strip() or None,
                            updated_mobile.strip() or None,
                            updated_aadhaar.strip() or None,
                            updated_status,
                            selected_id
                        )

                        success, message = execute_query(query, values)

                        if success:
                            st.success("Voter record updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Could not update voter: {message}")

    except mysql.connector.Error as error:
        st.error(f"Could not load voter records: {error}")


with tab_delete:
    st.subheader("Delete a Voter Record")

    st.warning(
        "Deleting a record is permanent for this database."
    )

    try:
        all_voters = fetch_voters()

        if not all_voters:
            st.info("There are no voter records to delete.")
        else:
            delete_options = {
                f"{v['Voter_ID']} — {v['Name']} "
                f"({v['EPIC_Number'] or 'No EPIC'})": v["Voter_ID"]
                for v in all_voters
            }

            delete_label = st.selectbox(
                "Select voter to delete",
                list(delete_options.keys()),
                key="delete_voter_selection"
            )

            delete_id = delete_options[delete_label]

            confirm_delete = st.checkbox(
                "I confirm that I want to permanently delete "
                "this demonstration record."
            )

            if st.button("Delete Selected Voter", type="primary"):
                if not confirm_delete:
                    st.error("Please confirm before deleting.")
                else:
                    success, message = execute_query(
                        "DELETE FROM voter WHERE Voter_ID = %s",
                        (delete_id,)
                    )

                    if success:
                        st.success("Voter record deleted.")
                        st.rerun()
                    else:
                        st.error(f"Could not delete voter: {message}")

    except mysql.connector.Error as error:
        st.error(f"Could not load voter records: {error}")


st.divider()

st.caption(
    "Academic demonstration only. Use fictional records. "
    "Statuses do not represent official identity checks "
    "or voter eligibility decisions."
)


# Purpose:
# Provides Create, Read, Search, Update, and Delete operations
# for voter records using parameterized MySQL queries.
# Requires login before displaying or modifying voter records.
