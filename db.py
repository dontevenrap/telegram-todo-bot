import sqlite3
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

DB_FILE = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    """Создает таблицу задач, если ее нет"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                text TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
    logger.info("Database initialized")

def add_task(user_id: str, text: str) -> bool:
    """Добавляет новую задачу пользователя в базу"""
    if not text.strip():
        logger.warning("Попытка добавить пустую задачу пользователем %s", user_id)
        return False
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (user_id, text) VALUES (?, ?)",
            (user_id, text)
        )
    logger.info("User %s added task: %s", user_id, text)
    return True

def get_tasks(user_id: str) -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, text, done FROM tasks WHERE user_id = ? ORDER BY done, id",
            (user_id,)
        )
        return [{"id": row[0], "text": row[1], "done": bool(row[2])} for row in cursor.fetchall()]

def toggle_task(user_id: str, task_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET done = 1 - done WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
    logger.info("User %s toggled task #%d", user_id, task_id)

def remove_task(user_id: str, task_id: int):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
    logger.info("User %s removed task #%d", user_id, task_id)
