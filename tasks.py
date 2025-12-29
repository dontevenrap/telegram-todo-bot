from typing import List, Dict
from db import init_db, add_task as db_add, get_tasks as db_get, toggle_task as db_toggle, remove_task as db_remove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

init_db()

def add_task(user_id: str, text: str):
    """Добавляет новую задачу пользователя"""
    db_add(user_id, text)

def get_tasks_list(user_id: str) -> List[Dict]:
    """Возвращает список задач пользователя"""
    return db_get(user_id)

def get_task_by_id(user_id: str, task_id: int) -> Dict | None:
    tasks_list = get_tasks_list(user_id)
    for t in tasks_list:
        if t["id"] == task_id:
            return t
    return None

def toggle_task(user_id: str, task_id: int):
    db_toggle(user_id, task_id)

def remove_task(user_id: str, task_id: int):
    db_remove(user_id, task_id)

def get_stats_text(user_id: str) -> str:
    tasks_list = get_tasks_list(user_id)
    total = len(tasks_list)
    done = sum(t["done"] for t in tasks_list)
    if total == 0:
        return "Список задач пуст 😕"
    percent = int(done / total * 100)
    bar_length = 20
    done_bar = "█" * int(bar_length * done / total)
    active_bar = "░" * (bar_length - len(done_bar))
    return (
        f"📊 Статистика:\n"
        f"Всего задач: {total}\n"
        f"Выполнено: {done}\n"
        f"Активно: {total - done}\n"
        f"[{done_bar}{active_bar}] {percent}%"
    )

def task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Отметить выполненной", callback_data=f"toggle:{task_id}")],
        [InlineKeyboardButton("Удалить", callback_data=f"remove:{task_id}")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ])
