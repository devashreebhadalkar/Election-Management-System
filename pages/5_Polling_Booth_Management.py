
import streamlit as st
import pandas as pd
import mysql.connector

from database import get_connection
from services.ui import apply_portal_style, show_portal_banner
from services.auth import require_login


st.set_page_config(
    page_title="Polling Booth Management | Election Management System",
    page_icon="🏫",
    layout="wide"
)

apply_portal_style()

# Require login before accessing polling booth records.
require_login()

show_portal_banner(
    "Polling Booth Management",
    "Manage and maintain demonstration polling booth records"
)

st.write(
    "View, search and maintain polling booth details in the database."
)

st.info(
    "Use fictional demo data for academic testing. "
    "These records do not represent official polling locations."
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
    "➕ Add Booth",
    "📋 View / Search",
    "✏️ Update Booth",
    "🗑️ Delete Booth"
])


# ADD BOOTH
with tab1:
    st.subheader("Add a Polling Booth")

    with st.form("add_booth_form"):
        booth_number = st.text_input("Booth Number")
        booth_name = st.text_input("Booth Name")
        constituency = st.text_input("Constituency")
        district = st.text_input("District")
        state = st.text_input("State")

        submitted = st.form_submit_button(
            "Add Booth",
            use_container_width=True
        )

        if submitted:
            if not all([
                booth_number.strip(),
                booth_name.strip(),
                constituency.strip(),
                district.strip(),
                state.strip()
            ]):
                st.error("Please fill in all fields.")
            else:
                result = run_query(
                    """
                    INSERT INTO polling_booth
                        (Booth_Number, Booth_Name, Constituency,
                         District, State)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        booth_number.strip(),
                        booth_name.strip(),
                        constituency.strip(),
                        district.strip(),
                        state.strip()
                    )
                )

                if result:
                    st.success("Polling booth added successfully!")
                    st.rerun()


# VIEW AND SEARCH
with tab2:
    st.subheader("View and Search Polling Booths")

    search_text = st.text_input(
        "Search by ID, Booth Number, Name, Constituency, District, or State",
        placeholder="Enter a booth number, name, district, or state..."
    )

    booths = run_query(
        """
        SELECT Booth_ID, Booth_Number, Booth_Name,
               Constituency, District, State
        FROM polling_booth
        WHERE CAST(Booth_ID AS CHAR) LIKE %s
           OR Booth_Number LIKE %s
           OR Booth_Name LIKE %s
           OR Constituency LIKE %s
           OR District LIKE %s
           OR State LIKE %s
        ORDER BY Booth_ID DESC
        """,
        tuple([f"%{search_text}%"] * 6),
        fetch=True
    )

    if booths is not None:
        st.dataframe(
            booths,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Records found: {len(booths)}")


# UPDATE BOOTH
with tab3:
    st.subheader("Update Polling Booth Details")

    booths = run_query(
        """
        SELECT Booth_ID, Booth_Number, Booth_Name,
               Constituency, District, State
        FROM polling_booth
        ORDER BY Booth_ID
        """,
        fetch=True
    )

    if booths is not None and not booths.empty:
        booth_ids = booths["Booth_ID"].tolist()

        selected_id = st.selectbox(
            "Select Booth ID",
            booth_ids,
            key="update_booth_id"
        )

        selected = booths[
            booths["Booth_ID"] == selected_id
        ].iloc[0]

        with st.form("update_booth_form"):
            new_number = st.text_input(
                "Booth Number",
                value=str(selected["Booth_Number"])
            )

            new_name = st.text_input(
                "Booth Name",
                value=str(selected["Booth_Name"])
            )

            new_constituency = st.text_input(
                "Constituency",
                value=str(selected["Constituency"])
            )

            new_district = st.text_input(
                "District",
                value=str(selected["District"])
            )

            new_state = st.text_input(
                "State",
                value=str(selected["State"])
            )

            update_clicked = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if update_clicked:
                if not all([
                    new_number.strip(),
                    new_name.strip(),
                    new_constituency.strip(),
                    new_district.strip(),
                    new_state.strip()
                ]):
                    st.error("Please fill in all fields.")
                else:
                    result = run_query(
                        """
                        UPDATE polling_booth
                        SET Booth_Number = %s,
                            Booth_Name = %s,
                            Constituency = %s,
                            District = %s,
                            State = %s
                        WHERE Booth_ID = %s
                        """,
                        (
                            new_number.strip(),
                            new_name.strip(),
                            new_constituency.strip(),
                            new_district.strip(),
                            new_state.strip(),
                            selected_id
                        )
                    )

                    if result:
                        st.success("Polling booth updated successfully!")
                        st.rerun()

    elif booths is not None:
        st.info("No polling booth records available.")


# DELETE BOOTH
with tab4:
    st.subheader("Delete a Polling Booth")

    booths = run_query(
        """
        SELECT Booth_ID, Booth_Number, Booth_Name,
               Constituency, District, State
        FROM polling_booth
        ORDER BY Booth_ID
        """,
        fetch=True
    )

    if booths is not None and not booths.empty:
        booth_ids = booths["Booth_ID"].tolist()

        delete_id = st.selectbox(
            "Select Booth ID to delete",
            booth_ids,
            key="delete_booth_id"
        )

        st.warning(
            f"You selected booth record ID {delete_id}. "
            "Deletion cannot be undone."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this demo record."
        )

        if st.button("Delete Booth", type="primary"):
            if confirm:
                result = run_query(
                    "DELETE FROM polling_booth WHERE Booth_ID = %s",
                    (delete_id,)
                )

                if result:
                    st.success("Polling booth deleted successfully!")
                    st.rerun()
            else:
                st.error("Please confirm before deleting.")

    elif booths is not None:
        st.info("No polling booth records available.")


# Purpose:
# Manages polling booth records using MySQL CRUD operations.
# Requires login before accessing polling booth records.
# Uses fictional demonstration data for academic testing.
