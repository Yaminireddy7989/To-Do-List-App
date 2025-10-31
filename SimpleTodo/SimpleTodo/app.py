
import sqlite3
from contextlib import closing
import pandas as pd
import streamlit as st

DB_PATH = "simple_todo.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()

def add_task(title, description):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title.strip(), (description or "").strip()))
        conn.commit()

def get_tasks():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, created_at FROM tasks ORDER BY id DESC")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(rows, columns=cols)

def main():
    st.set_page_config(page_title="Simple To-Do", page_icon="📝", layout="centered")
    st.title("📝 Simple To-Do")
    st.caption("Add tasks → View table. Super minimal.")

    init_db()

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title*", placeholder="e.g., Call client")
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not title or not title.strip():
                st.error("Title is required.")
            else:
                add_task(title, description)
                st.success("Task added ✅")

    df = get_tasks()
    if df.empty:
        st.info("No tasks yet — add your first one above.")
    else:
        if "created_at" in df.columns:
            df["created_at"] = df["created_at"].astype(str).str.replace("T", " ").str[:19]
        st.write("### 📋 Tasks")
        st.dataframe(df, use_container_width=True, height=400)

if __name__ == "__main__":
    main()
