
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Claim & Objection Management",
    page_icon="📑",
    layout="wide"
)

apply_portal_style()

# Require login before accessing claim and objection records.
require_login()

show_portal_banner(
    "Claim & Objection Management",
    "Manage and track demo claims and objections"
)

st.caption(
    "Academic project demonstration using fictional data. "
    "This module does not make official election decisions."
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


claim_types = [
    "Inclusion",
    "Correction",
    "Deletion",
    "Objection",
    "Other"
]

claim_statuses = [
    "Pending",
    "Under Review",
    "Accepted",
    "Rejected"
]


tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add Claim",
    "📋 View / Search",
    "✏️ Update Claim",
    "🗑️ Delete Claim"
])


# ADD CLAIM
with tab1:
    st.subheader("Add a Claim or Objection")
    st.write("Enter the details of a fictional demo claim.")

    with st.form("add_claim_form"):
        claim_type = st.selectbox("Claim Type", claim_types)

        description = st.text_area(
            "Description",
            placeholder="Enter a brief description of the demo claim..."
        )

        claim_date = st.date_input("Claim Date")
        status = st.selectbox("Status", claim_statuses)

        submitted = st.form_submit_button(
            "Add Claim",
            use_container_width=True
        )

        if submitted:
            if not description.strip():
                st.error("Please enter a description.")
            else:
                result = run_query(
                    """
                    INSERT INTO claim_objection
                        (Claim_Type, Description, Claim_Date, Status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        claim_type,
                        description.strip(),
                        claim_date,
                        status
                    )
                )

                if result:
                    st.success("Claim record added successfully!")
                    st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Claims")

    search_text = st.text_input(
        "Search by Claim ID, Type, Description, or Status",
        placeholder="Enter a claim ID, type, keyword, or status..."
    )

    claims = run_query(
        """
        SELECT Claim_ID, Claim_Type, Description, Claim_Date, Status
        FROM claim_objection
        WHERE CAST(Claim_ID AS CHAR) LIKE %s
           OR Claim_Type LIKE %s
           OR Description LIKE %s
           OR Status LIKE %s
        ORDER BY Claim_ID DESC
        """,
        tuple([f"%{search_text}%"] * 4),
        fetch=True
    )

    if claims is not None:
        st.dataframe(
            claims,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Records found: {len(claims)}")


# UPDATE CLAIM
with tab3:
    st.subheader("Update Claim Details")

    claims = run_query(
        """
        SELECT Claim_ID, Claim_Type, Description, Claim_Date, Status
        FROM claim_objection
        ORDER BY Claim_ID
        """,
        fetch=True
    )

    if claims is not None and not claims.empty:
        claim_ids = claims["Claim_ID"].tolist()

        selected_id = st.selectbox(
            "Select Claim ID",
            claim_ids,
            key="update_claim_id"
        )

        selected = claims[
            claims["Claim_ID"] == selected_id
        ].iloc[0]

        current_type = selected["Claim_Type"]
        type_index = (
            claim_types.index(current_type)
            if current_type in claim_types
            else 0
        )

        current_status = selected["Status"]
        status_index = (
            claim_statuses.index(current_status)
            if current_status in claim_statuses
            else 0
        )

        with st.form("update_claim_form"):
            new_type = st.selectbox(
                "Claim Type",
                claim_types,
                index=type_index
            )

            new_description = st.text_area(
                "Description",
                value=(
                    ""
                    if pd.isna(selected["Description"])
                    else str(selected["Description"])
                )
            )

            current_date = selected["Claim_Date"]

            if pd.isna(current_date):
                current_date = pd.Timestamp.today().date()
            elif hasattr(current_date, "date"):
                current_date = current_date.date()

            new_date = st.date_input(
                "Claim Date",
                value=current_date
            )

            new_status = st.selectbox(
                "Status",
                claim_statuses,
                index=status_index
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                if not new_description.strip():
                    st.error("Description cannot be empty.")
                else:
                    result = run_query(
                        """
                        UPDATE claim_objection
                        SET Claim_Type = %s,
                            Description = %s,
                            Claim_Date = %s,
                            Status = %s
                        WHERE Claim_ID = %s
                        """,
                        (
                            new_type,
                            new_description.strip(),
                            new_date,
                            new_status,
                            selected_id
                        )
                    )

                    if result:
                        st.success("Claim record updated successfully!")
                        st.rerun()

    else:
        st.info("No claim records are available.")


# DELETE CLAIM
with tab4:
    st.subheader("Delete a Claim Record")

    claims = run_query(
        """
        SELECT Claim_ID, Claim_Type, Description, Claim_Date, Status
        FROM claim_objection
        ORDER BY Claim_ID
        """,
        fetch=True
    )

    if claims is not None and not claims.empty:
        claim_ids = claims["Claim_ID"].tolist()

        delete_id = st.selectbox(
            "Select Claim ID to delete",
            claim_ids,
            key="delete_claim_id"
        )

        st.warning(
            f"You selected claim record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Claim", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM claim_objection WHERE Claim_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Claim record deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    else:
        st.info("No claim records are available.")
