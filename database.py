
import os

import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv(
            "DB_NAME",
            "election_management_system"
        )
    )


def test_connection():
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection.is_connected():
            st.success("Connected to MySQL successfully!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            st.write("Tables found in the database:")

            for table in tables:
                st.write(f"- {table[0]}")

    except mysql.connector.Error as error:
        st.error(f"MySQL connection failed: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# Purpose: Connect Python to MySQL and display the available tables.
 