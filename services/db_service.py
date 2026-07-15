import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            client_case_id TEXT,
            original_filename TEXT,
            stored_filename TEXT,
            upload_path TEXT,
            preview_path TEXT,
            result_image_path TEXT,
            report_path TEXT,
            modality TEXT,
            notes TEXT,
            score REAL,
            status TEXT,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def insert_case(case_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO cases (
            case_id,
            client_case_id,
            original_filename,
            stored_filename,
            upload_path,
            preview_path,
            result_image_path,
            report_path,
            modality,
            notes,
            score,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_data["case_id"],
            case_data.get("client_case_id"),
            case_data["original_filename"],
            case_data["stored_filename"],
            case_data["upload_path"],
            case_data["preview_path"],
            case_data["result_image_path"],
            case_data["report_path"],
            case_data.get("modality"),
            case_data.get("notes"),
            case_data.get("score"),
            case_data.get("status"),
            case_data.get("created_at"),
        ),
    )

    conn.commit()
    conn.close()


def get_case_by_case_id(case_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cases
        WHERE case_id = ?
        """,
        (case_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


def list_cases(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM cases
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]