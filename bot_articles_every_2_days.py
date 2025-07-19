# bot_articles_every_2_days.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import time, timedelta
import asyncio

import os
TOKEN = os.environ["TOKEN"]

# Простий список статей
articles = [
    "Стаття 1: Вступ до медитації — як працює розум.",
    "Стаття 2: Дихання як інструмент заспокоєння.",
    "Стаття 3: Як зменшити стрес через усвідомленість.",
    "Стаття 4: Парасимпатична нервова система: що це і як її активувати.",
    "Стаття 5: Роль фізичних вправ у подоланні тривожності."
]

# Прогрес користувача: chat_id -> index статті
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_progress[chat_id] = 0  # Починаємо з першої статті
    await update.message.reply_text("Привіт! Я надсилатиму тобі нову статтю кожні 2 дні 📰")

    # Розклад надсилання: щодня, але логіка перевіряє кожні 2 дні
    context.job_queue.run_repeating(
        send_article_if_due,
        interval=timedelta(days=1),  # перевіряємо щодня
        first=timedelta(seconds=5),  # початок через 5 секунд
        chat_id=chat_id,
        name=str(chat_id)
    )

# Функція надсилання статті
async def send_article_if_due(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    idx = user_progress.get(chat_id, 0)

    # зберігаємо останній час надсилання в job.context
    if 'last_sent' not in context.job.context:
        context.job.context['last_sent'] = None

    now = context.job_queue._dispatcher.time_provider()
    last_sent = context.job.context['last_sent']

    # якщо пройшло більше ніж 1 день і є ще статті
    if (last_sent is None or (now - last_sent) >= timedelta(days=2)) and idx < len(articles):
        await context.bot.send_message(chat_id=chat_id, text=articles[idx])
        user_progress[chat_id] = idx + 1
        context.job.context['last_sent'] = now
    elif idx >= len(articles):
        await context.bot.send_message(chat_id=chat_id, text="🟢 Всі статті надіслано. Дякую, що читав(ла)!")

# Головна функція
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    await app.initialize()
    await app.start()
    print("Бот працює...")
    await asyncio.Event().wait()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
