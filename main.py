from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
)
from datetime import datetime, timedelta
import asyncio
import os

# ✅ Flask-сервер
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "✅ Бот працює!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Для PythonAnywhere або Replit
    print(f"🌐 Flask сервер стартує на порту {port}")
    flask_app.run(host='0.0.0.0', port=port)

# ✅ Статті
articles = [
    "Стаття 1: Вступ до медитації — як працює розум.",
    "Стаття 2: Дихання як інструмент заспокоєння.",
    "Стаття 3: Як зменшити стрес через усвідомленість.",
    "Стаття 4: Парасимпатична нервова система: що це і як її активувати.",
    "Стаття 5: Роль фізичних вправ у подоланні тривожності."
]

user_progress = {}

# ✅ /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_progress[chat_id] = {
        'index': 1,
        'last_sent': datetime.now()
    }

    await update.message.reply_text("Привіт! Я надсилатиму тобі нову статтю кожні 5 хвилин 📰")
    await context.bot.send_message(chat_id=chat_id, text=articles[0])

    context.job_queue.run_repeating(
        send_article_if_due,
        interval=timedelta(minutes=5),
        first=timedelta(minutes=5),
        chat_id=chat_id
    )

# ✅ Надсилання статей
async def send_article_if_due(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    progress = user_progress.get(chat_id)

    if not progress:
        return

    now = datetime.now()
    idx = progress['index']
    last_sent = progress['last_sent']

    if idx < len(articles) and (now - last_sent) >= timedelta(minutes=5):
        await context.bot.send_message(chat_id=chat_id, text=articles[idx])
        user_progress[chat_id] = {
            'index': idx + 1,
            'last_sent': now
        }
    elif idx >= len(articles):
        await context.bot.send_message(
            chat_id=chat_id,
            text="🟢 Всі статті надіслано. Дякую, що читав(ла)!"
        )

# ✅ JobQueue ініціалізація
async def setup_jobqueue(app):
    if app.job_queue is None:
        app.job_queue = JobQueue()
        await app.job_queue.set_application(app)
        app.job_queue.start()

# ✅ Запуск бота
async def run_bot():
    app_bot = (
        ApplicationBuilder()
        .token("7554974295:AAF9p2Ve9vL-y-Yt9zJ_FoMywmbymHwlz6s")  # ⛔ не залишай токен у відкритому коді
        .post_init(setup_jobqueue)
        .build()
    )

    app_bot.add_handler(CommandHandler("start", start))
    print("✅ Бот запущено")
    await app_bot.run_polling()

# ✅ Старт
if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(run_bot())
