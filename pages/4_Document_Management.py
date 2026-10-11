
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Document Management | Election Management System",
    page_icon="📁",
    layout="wide"
)

apply_portal_style()

# Require login before accessing document records.
require_login()

show_portal_banner(
    "Document Management",
    "Manage, search and maintain document records"
)

st.write(
    "Maintain document details and their recorded verification status."
)

st.info(
    "Use fictional demo records only. This page tracks document details "
    "and status; it does not verify real identity documents."
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


document_types = [
    "Identity Proof",
    "Address Proof",
    "Age Proof",
    "Other"
]

verification_statuses = [
    "Pending",
    "Verified",
    "Rejected"
]

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Document",
    "📋 View / Search",
    "✏️ Update Status",
    "🗑️ Delete Document"
])


# 1. ADD DOCUMENT
with tab1:
    st.subheader("Add a Document Record")

    with st.form("add_document_form"):
        document_type = st.selectbox(
            "Document Type",
            document_types
        )

        upload_date = st.date_input("Record Date")

        verification_status = st.selectbox(
            "Verification Status",
            verification_statuses
        )

        submitted = st.form_submit_button(
            "Add Document",
            use_container_width=True
        )

        if submitted:
            result = run_query(
                """
                INSERT INTO document
                    (Document_Type, Upload_Date, Verification_Status)
                VALUES (%s, %s, %s)
                """,
                (
                    document_type,
                    upload_date,
                    verification_status
                )
            )

            if result:
                st.success("Document record added successfully!")
                st.rerun()


# 2. VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Document Records")

    search_text = st.text_input(
        "Search by Document ID, Type, or Status",
        placeholder="Enter an ID, document type, or status..."
    )

    documents = run_query(
        """
        SELECT Document_ID, Document_Type, Upload_Date,
               Verification_Status
        FROM document
        WHERE CAST(Document_ID AS CHAR) LIKE %s
           OR Document_Type LIKE %s
           OR Verification_Status LIKE %s
        ORDER BY Document_ID DESC
        """,
        (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ),
        fetch=True
    )

    if documents is not None:
        st.dataframe(
            documents,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Records found: {len(documents)}")


# 3. UPDATE DOCUMENT
with tab3:
    st.subheader("Update Document Details")

    documents = run_query(
        """
        SELECT Document_ID, Document_Type, Upload_Date,
               Verification_Status
        FROM document
        ORDER BY Document_ID
        """,
        fetch=True
    )

    if documents is not None and not documents.empty:
        document_ids = documents["Document_ID"].tolist()

        selected_id = st.selectbox(
            "Select Document ID",
            document_ids,
            key="update_document_id"
        )

        selected = documents[
            documents["Document_ID"] == selected_id
        ].iloc[0]

        current_type = selected["Document_Type"]

        type_index = (
            document_types.index(current_type)
            if current_type in document_types
            else 0
        )

        current_status = selected["Verification_Status"]

        status_index = (
            verification_statuses.index(current_status)
            if current_status in verification_statuses
            else 0
        )

        with st.form("update_document_form"):
            new_type = st.selectbox(
                "Document Type",
                document_types,
                index=type_index
            )

            current_date = selected["Upload_Date"]

            if pd.isna(current_date):
                current_date = pd.Timestamp.today().date()
            elif hasattr(current_date, "date"):
                current_date = current_date.date()

            new_date = st.date_input(
                "Record Date",
                value=current_date
            )

            new_status = st.selectbox(
                "Verification Status",
                verification_statuses,
                index=status_index
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                result = run_query(
                    """
                    UPDATE document
                    SET Document_Type = %s,
                        Upload_Date = %s,
                        Verification_Status = %s
                    WHERE Document_ID = %s
                    """,
                    (new_type, new_date, new_status, selected_id)
                )

                if result:
                    st.success("Document record updated successfully!")
                    st.rerun()

    elif documents is not None:
        st.info("No document records are available.")


# 4. DELETE DOCUMENT
with tab4:
    st.subheader("Delete a Document Record")

    documents = run_query(
        """
        SELECT Document_ID, Document_Type, Upload_Date,
               Verification_Status
        FROM document
        ORDER BY Document_ID
        """,
        fetch=True
    )

    if documents is not None and not documents.empty:
        document_ids = documents["Document_ID"].tolist()

        delete_id = st.selectbox(
            "Select Document ID to delete",
            document_ids,
            key="delete_document_id"
        )

        st.warning(
            f"You selected document record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Document", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM document WHERE Document_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Document record deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    elif documents is not None:
        st.info("No document records are available.")


# Purpose:
# Manages document records using MySQL CRUD operations.
# Requires login before accessing document records.
# Uses fictional demonstration data for academic testing.
