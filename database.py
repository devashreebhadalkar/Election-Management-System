import os
from pathlib import Path

import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Read Streamlit Cloud Secrets first, then use local .env values.
def get_setting(key, default=None):
    try:
        value = st.secrets.get(key)
        if value is not None and str(value).strip():
            return value
    except Exception:
        pass

    return os.getenv(key, default)


def get_connection():
    host = get_setting("DB_HOST", "localhost")
    port = int(get_setting("DB_PORT", "3306"))
    user = get_setting("DB_USER", "root")
    password = get_setting("DB_PASSWORD", "")
    database = get_setting(
        "DB_NAME",
        "election_management_system"
    )

    connection_options = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": 15,
    }

    # Verify the TiDB server's TLS certificate and hostname.
    if host != "localhost" and host != "127.0.0.1":
        ca_file = Path(__file__).resolve().parent / "tidb_ca.pem"

        if not ca_file.is_file():
            raise FileNotFoundError(
                "tidb_ca.pem is missing from the project folder."
            )

        connection_options.update({
            "ssl_ca": str(ca_file),
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        })

    return mysql.connector.connect(**connection_options)


def test_connection():
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection.is_connected():
            st.success("Connected to the database successfully!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            st.write("Tables found in the database:")

            if tables:
                for table in tables:
                    st.write(f"- {table[0]}")
            else:
                st.warning("No tables were found.")

    except (mysql.connector.Error, OSError, ValueError) as error:
        st.error(f"Database connection failed: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# Purpose:
# Connect the Streamlit app to local MySQL or cloud-hosted TiDB.
# Read credentials from Streamlit Secrets or the local .env file.
# Verify TLS for remote database connections and list available tables.
