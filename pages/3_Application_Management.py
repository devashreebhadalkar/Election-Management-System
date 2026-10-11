
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Application Management | Election Management System",
    page_icon="📄",
    layout="wide"
)

apply_portal_style()

# Require login before accessing application records.
require_login()

show_portal_banner(
    "Application Management",
    "Manage, search, update and review application records"
)

st.write(
    "Maintain application records for your academic Election Management System."
)

st.info(
    "Use fictional demo data only. This page is for academic project testing."
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
            columns = [item[0] for item in cursor.description]
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


tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Application",
    "📋 View / Search",
    "✏️ Update Application",
    "🗑️ Delete Application"
])


# ADD APPLICATION
with tab1:
    st.subheader("Add a New Application")

    with st.form("add_application_form"):
        form_type = st.selectbox(
            "Form Type",
            [
                "New Registration",
                "Correction",
                "Address Change",
                "Deletion",
                "Other"
            ]
        )

        application_date = st.date_input("Application Date")

        status = st.selectbox(
            "Application Status",
            ["Pending", "Under Review", "Approved", "Rejected"]
        )

        submitted = st.form_submit_button(
            "Add Application",
            use_container_width=True
        )

        if submitted:
            result = run_query(
                """
                INSERT INTO application
                    (Form_Type, Application_Date, Status)
                VALUES (%s, %s, %s)
                """,
                (form_type, application_date, status)
            )

            if result:
                st.success("Application added successfully!")
                st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Applications")

    search_text = st.text_input(
        "Search by Application ID, Form Type, or Status",
        placeholder="Enter an ID, form type, or status..."
    )

    applications = run_query(
        """
        SELECT Application_ID, Form_Type, Application_Date, Status
        FROM application
        WHERE CAST(Application_ID AS CHAR) LIKE %s
           OR Form_Type LIKE %s
           OR Status LIKE %s
        ORDER BY Application_ID DESC
        """,
        (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ),
        fetch=True
    )

    if applications is not None:
        st.dataframe(
            applications,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Records found: {len(applications)}")


# UPDATE APPLICATION
with tab3:
    st.subheader("Update an Application")

    all_applications = run_query(
        """
        SELECT Application_ID, Form_Type, Application_Date, Status
        FROM application
        ORDER BY Application_ID
        """,
        fetch=True
    )

    if all_applications is not None and not all_applications.empty:
        application_ids = all_applications["Application_ID"].tolist()

        selected_id = st.selectbox(
            "Select Application ID",
            application_ids,
            key="update_application_id"
        )

        selected = all_applications[
            all_applications["Application_ID"] == selected_id
        ].iloc[0]

        form_options = [
            "New Registration",
            "Correction",
            "Address Change",
            "Deletion",
            "Other"
        ]

        with st.form("update_application_form"):
            new_form_type = st.selectbox(
                "Form Type",
                form_options,
                index=(
                    form_options.index(selected["Form_Type"])
                    if selected["Form_Type"] in form_options
                    else 0
                )
            )

            current_date = selected["Application_Date"]

            if pd.isna(current_date):
                current_date = pd.Timestamp.today().date()
            elif hasattr(current_date, "date"):
                current_date = current_date.date()

            new_date = st.date_input(
                "Application Date",
                value=current_date
            )

            status_options = [
                "Pending",
                "Under Review",
                "Approved",
                "Rejected"
            ]

            current_status = selected["Status"]

            status_index = (
                status_options.index(current_status)
                if current_status in status_options
                else 0
            )

            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_index
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                result = run_query(
                    """
                    UPDATE application
                    SET Form_Type = %s,
                        Application_Date = %s,
                        Status = %s
                    WHERE Application_ID = %s
                    """,
                    (new_form_type, new_date, new_status, selected_id)
                )

                if result:
                    st.success("Application updated successfully!")
                    st.rerun()

    elif all_applications is not None:
        st.info("No applications available to update.")


# DELETE APPLICATION
with tab4:
    st.subheader("Delete an Application")

    delete_data = run_query(
        """
        SELECT Application_ID, Form_Type, Application_Date, Status
        FROM application
        ORDER BY Application_ID
        """,
        fetch=True
    )

    if delete_data is not None and not delete_data.empty:
        delete_ids = delete_data["Application_ID"].tolist()

        delete_id = st.selectbox(
            "Select Application ID to delete",
            delete_ids,
            key="delete_application_id"
        )

        st.warning(
            f"You selected application ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Application", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM application WHERE Application_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Application deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    elif delete_data is not None:
        st.info("No applications available to delete.")


# Purpose:
# Manages application records using MySQL CRUD operations.
# Requires login before displaying or modifying application records.
# Uses fictional demonstration data for academic testing.
