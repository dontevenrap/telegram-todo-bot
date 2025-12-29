import os
import random
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import tasks

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main_keyboard() -> list[list[str]]:
    return [["➕ Добавить задачу"], ["📋 Список задач", "📊 Статистика"]]

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(main_keyboard(), resize_keyboard=True)

def task_keyboard(user_id: str) -> InlineKeyboardMarkup:
    tasks_list = tasks.get_tasks_list(user_id)
    kb = [[
        tasks.task_action_keyboard(t["id"]).inline_keyboard[0][0]
    ] for t in tasks_list]
    return InlineKeyboardMarkup(kb)

def user_tasks_exist(user_id: str) -> bool:
    return bool(tasks.get_tasks_list(user_id))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User %s started bot", update.effective_user.id)
    await update.message.reply_text("Привет! Выбери действие:", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    if context.user_data.get("adding"):
        if text == "❌ Отменить":
            context.user_data["adding"] = False
            await update.message.reply_text("Добавление задачи отменено.", reply_markup=get_main_keyboard())
            return
        tasks.add_task(user_id, text)
        context.user_data["adding"] = False
        await update.message.reply_text(f"Задача '{text}' добавлена!", reply_markup=get_main_keyboard())
        return

    if text == "➕ Добавить задачу":
        await update.message.reply_text("Отправь текст новой задачи:", reply_markup=ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True))
        context.user_data["adding"] = True
    elif text == "📋 Список задач":
        if not user_tasks_exist(user_id):
            await update.message.reply_text("Список задач пуст 😕", reply_markup=ReplyKeyboardMarkup([["➕ Добавить задачу"]], resize_keyboard=True))
        else:
            await show_task_list(update, user_id)
    elif text == "📊 Статистика":
        await show_stats(update, user_id)
    else:
        await update.message.reply_text("Используй кнопки меню:", reply_markup=get_main_keyboard())

async def show_task_list(update_or_query, user_id: str):
    tasks_list = tasks.get_tasks_list(user_id)
    text = "\n".join([f"{'✓' if t['done'] else '•'} {t['text']}" for t in tasks_list])
    message = getattr(update_or_query, "message", update_or_query)
    await message.reply_text(text, reply_markup=task_keyboard(user_id))

async def show_stats(update: Update, user_id: str):
    await update.message.reply_text(tasks.get_stats_text(user_id), reply_markup=get_main_keyboard())

async def handle_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data == "back":
        await show_task_list(query, user_id)
        return

    if ":" in data:
        action, task_id = data.split(":")
        task_id = int(task_id)
        if action == "toggle":
            tasks.toggle_task(user_id, task_id)
        elif action == "remove":
            tasks.remove_task(user_id, task_id)
    else:
        task_id = int(data)
        task = tasks.get_task_by_id(user_id, task_id)
        if task:
            await query.edit_message_text(f"📌 {task['text']}", reply_markup=tasks.task_action_keyboard(task_id))
            return
    await show_task_list(query, user_id)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(handle_task_callback))

print("Бот запущен...")
logger.info("Bot started")
app.run_polling(allowed_updates=Update.ALL_TYPES)
