import os
import sqlite3


DB_PATH = "database/campus.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    os.makedirs(
        os.path.dirname(
            DB_PATH
        ),
        exist_ok=True,
    )

    return sqlite3.connect(
        DB_PATH
    )


# =========================================================
# TABLE
# =========================================================

def create_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_name TEXT,
            chunk_no INTEGER,
            chunk_text TEXT
        )
        """
    )

    conn.commit()

    conn.close()


# =========================================================
# PDF SİL
# =========================================================

def delete_pdf(
    pdf_name
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM chunks
        WHERE pdf_name = ?
        """,
        (
            pdf_name,
        ),
    )

    conn.commit()

    conn.close()


# =========================================================
# CHUNK KAYDET
# =========================================================

def save_chunks(
    pdf_name,
    chunks,
):

    conn = get_connection()

    cursor = conn.cursor()

    for i, chunk in enumerate(
        chunks
    ):

        cursor.execute(
            """
            INSERT INTO chunks
            (
                pdf_name,
                chunk_no,
                chunk_text
            )
            VALUES (?, ?, ?)
            """,
            (
                pdf_name,
                i + 1,
                chunk,
            ),
        )

    conn.commit()

    conn.close()


# =========================================================
# CHUNKLARI GETİR
# =========================================================

def get_chunks():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            pdf_name,
            chunk_no,
            chunk_text
        FROM chunks
        ORDER BY
            pdf_name,
            chunk_no
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows