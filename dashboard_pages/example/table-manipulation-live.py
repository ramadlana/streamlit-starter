import json
import ssl
import sqlite3
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd
import streamlit as st

API_URL = "https://jsonplaceholder.typicode.com/todos?_limit=25"
ROOT_DIR = Path(__file__).resolve().parents[2]
INSTANCE_DIR = ROOT_DIR / "instance"
DB_PATH = INSTANCE_DIR / "table_live.db"
TABLE_NAME = "todos"
TABLE_COLUMNS = ["id", "userId", "title", "completed"]


def ensure_db() -> None:
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                userId INTEGER NOT NULL,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL CHECK (completed IN (0, 1))
            )
            """
        )
        conn.commit()


def fetch_from_api() -> tuple[pd.DataFrame, bool]:
    insecure = False
    try:
        with urlopen(API_URL, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        insecure = True
        insecure_context = ssl._create_unverified_context()
        with urlopen(API_URL, timeout=20, context=insecure_context) as response:
            data = json.loads(response.read().decode("utf-8"))

    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=TABLE_COLUMNS), insecure
    df = df[TABLE_COLUMNS].copy()
    df["completed"] = df["completed"].astype(bool)
    return df, insecure


def load_from_db() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            f"SELECT id, userId, title, completed FROM {TABLE_NAME} ORDER BY id",
            conn,
        )
    if df.empty:
        return pd.DataFrame(columns=TABLE_COLUMNS)
    df["completed"] = df["completed"].astype(bool)
    return df


def save_to_db(df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    payload = df[TABLE_COLUMNS].copy()
    payload["id"] = pd.to_numeric(payload["id"], errors="coerce")
    payload["userId"] = pd.to_numeric(payload["userId"], errors="coerce")
    payload["title"] = payload["title"].fillna("").astype(str).str.strip()
    payload["completed"] = payload["completed"].fillna(False).astype(bool)

    payload = payload.dropna(subset=["id", "userId"])
    payload = payload[payload["title"] != ""]
    payload["id"] = payload["id"].astype(int)
    payload["userId"] = payload["userId"].astype(int)
    payload["completed"] = payload["completed"].astype(int)
    payload = payload.drop_duplicates(subset=["id"], keep="last")

    rows = [
        (int(row.id), int(row.userId), str(row.title), int(row.completed))
        for row in payload.itertuples(index=False)
    ]

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            f"""
            INSERT INTO {TABLE_NAME} (id, userId, title, completed)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                userId = excluded.userId,
                title = excluded.title,
                completed = excluded.completed
            """,
            rows,
        )
        conn.commit()
    return len(rows)


def init_state() -> None:
    if "table_df" not in st.session_state:
        st.session_state.table_df = pd.DataFrame(columns=TABLE_COLUMNS)


def main() -> None:
    st.set_page_config(page_title="Table Edit Live", page_icon="🧮", layout="wide")
    st.title("Live Table Manipulation with SQLite")
    st.caption("Fetch JSONPlaceholder data, edit it live, and persist it to SQLite.")

    ensure_db()
    init_state()

    col1, col2, col3 = st.columns(3)

    if col1.button("Fetch from API", width="stretch"):
        try:
            table_df, insecure = fetch_from_api()
            st.session_state.table_df = table_df
            st.success("Data loaded from JSONPlaceholder.")
            if insecure and not st.session_state.get("ssl_warning_shown", False):
                st.warning(
                    "SSL certificate verification failed in this environment. "
                    "Retried without certificate verification for local development."
                )
                st.session_state.ssl_warning_shown = True
        except URLError as exc:
            st.error(f"Failed to fetch from API: {exc}")

    if col2.button("Load from SQLite", width="stretch"):
        st.session_state.table_df = load_from_db()
        st.success(f"Loaded {len(st.session_state.table_df)} rows from SQLite.")

    if col3.button("Save to SQLite", width="stretch"):
        saved_count = save_to_db(st.session_state.table_df)
        st.success(f"Saved {saved_count} rows to {DB_PATH}.")

    edited_df = st.data_editor(
        st.session_state.table_df,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "id": st.column_config.NumberColumn("ID", min_value=1, step=1),
            "userId": st.column_config.NumberColumn("User ID", min_value=1, step=1),
            "title": st.column_config.TextColumn("Title"),
            "completed": st.column_config.CheckboxColumn("Completed"),
        },
        hide_index=True,
        key="live_table_editor",
    )

    st.session_state.table_df = edited_df
    st.info(f"Current rows in editor: {len(edited_df)}")


if __name__ == "__main__":
    main()
