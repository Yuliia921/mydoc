import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from generate_pdf import generate_pdf
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
user_data = {}

FIELDS = [
    "ФИО", "Последняя менструация", "Положение матки",
    "Размер плодного яйца", "Размер эмбриона", "Желточный мешок",
    "Сердцебиение и ЧСС", "Расположение хориона", "Желтое тело",
    "Дополнительные данные", "Заключение", "Рекомендации"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {"шаг": 0, "поля": {}}
    await update.message.reply_text("🌸 УЗИ для беременных — введите ФИО пациента:", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if chat_id not in user_data:
        await update.message.reply_text("Пожалуйста, начните с /start 🌸", disable_web_page_preview=True)
        return

    data = user_data[chat_id]
    шаг = data["шаг"]
    if шаг < len(FIELDS):
        data["поля"][FIELDS[шаг]] = text
        data["шаг"] += 1

    if data["шаг"] < len(FIELDS):
        await update.message.reply_text(f"Введите {FIELDS[data['шаг']]}:", disable_web_page_preview=True)
    else:
        filepath = generate_pdf(data["поля"], "УЗИ для беременных")
        with open(filepath, "rb") as f:
            await update.message.reply_document(
                document=BytesIO(f.read()),
                filename=os.path.basename(filepath),
                caption="Протокол УЗИ 🌸"
            )
        del user_data[chat_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
