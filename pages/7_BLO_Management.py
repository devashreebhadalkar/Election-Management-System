
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="BLO Management | Election Management System",
    page_icon="👤",
    layout="wide"
)

apply_portal_style()

# Require login before accessing BLO records.
require_login()

show_portal_banner(
    "BLO Management",
    "Manage and maintain Booth Level Officer records"
)

st.write(
    "View, search, add, update and delete BLO records."
)

st.info(
    "Use fictional demo records for academic project testing."
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


tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Add BLO",
    "📋 View / Search",
    "✏️ Update BLO",
    "🗑️ Delete BLO"
])


# ADD BLO
with tab1:
    st.subheader("Add a Booth Level Officer")

    with st.form("add_blo_form"):
        name = st.text_input("BLO Name")
        mobile = st.text_input("Mobile Number", max_chars=15)

        submitted = st.form_submit_button(
            "Add BLO",
            use_container_width=True
        )

        if submitted:
            if not name.strip() or not mobile.strip():
                st.error("Please enter the BLO name and mobile number.")
            else:
                result = run_query(
                    """
                    INSERT INTO BLO (Name, Mobile_Number)
                    VALUES (%s, %s)
                    """,
                    (name.strip(), mobile.strip())
                )

                if result:
                    st.success("BLO record added successfully!")
                    st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search BLO Records")

    search_text = st.text_input(
        "Search by BLO ID, Name, or Mobile Number",
        placeholder="Enter an ID, name, or mobile number..."
    )

    blos = run_query(
        """
        SELECT ELO_ID, Name, Mobile_Number
        FROM BLO
        WHERE CAST(ELO_ID AS CHAR) LIKE %s
           OR Name LIKE %s
           OR Mobile_Number LIKE %s
        ORDER BY ELO_ID DESC
        """,
        tuple([f"%{search_text}%"] * 3),
        fetch=True
    )

    if blos is not None:
        st.dataframe(
            blos,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Records found: {len(blos)}")


# UPDATE BLO
with tab3:
    st.subheader("Update BLO Details")

    blos = run_query(
        """
        SELECT ELO_ID, Name, Mobile_Number
        FROM BLO
        ORDER BY ELO_ID
        """,
        fetch=True
    )

    if blos is not None and not blos.empty:
        blo_ids = blos["ELO_ID"].tolist()

        selected_id = st.selectbox(
            "Select BLO ID",
            blo_ids,
            key="update_blo_id"
        )

        selected = blos[
            blos["ELO_ID"] == selected_id
        ].iloc[0]

        with st.form("update_blo_form"):
            new_name = st.text_input(
                "BLO Name",
                value=str(selected["Name"])
            )

            new_mobile = st.text_input(
                "Mobile Number",
                value=str(selected["Mobile_Number"]),
                max_chars=15
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                if not new_name.strip() or not new_mobile.strip():
                    st.error("Please fill in both fields.")
                else:
                    result = run_query(
                        """
                        UPDATE BLO
                        SET Name = %s, Mobile_Number = %s
                        WHERE ELO_ID = %s
                        """,
                        (
                            new_name.strip(),
                            new_mobile.strip(),
                            selected_id
                        )
                    )

                    if result:
                        st.success("BLO record updated successfully!")
                        st.rerun()

    elif blos is not None:
        st.info("No BLO records are available.")


# DELETE BLO
with tab4:
    st.subheader("Delete a BLO Record")

    blos = run_query(
        """
        SELECT ELO_ID, Name, Mobile_Number
        FROM BLO
        ORDER BY ELO_ID
        """,
        fetch=True
    )

    if blos is not None and not blos.empty:
        blo_ids = blos["ELO_ID"].tolist()

        delete_id = st.selectbox(
            "Select BLO ID to delete",
            blo_ids,
            key="delete_blo_id"
        )

        st.warning(
            f"You selected BLO record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete BLO", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM BLO WHERE ELO_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("BLO record deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    elif blos is not None:
        st.info("No BLO records are available.")


# Purpose:
# Manages BLO records using MySQL CRUD operations.
# Requires login before accessing BLO records.
# Uses fictional demonstration data for academic testing.
