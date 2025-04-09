import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
from generate_pdf import generate_pdf
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
user_data = {}

FIELDS_ZAKL = ["ФИО", "Возраст", "Диагноз", "Обследование", "Рекомендации"]
FIELDS_UZI = [
    "ФИО", "Последняя менструация", "Положение матки", "Размер плодного яйца", "Размер эмбриона",
    "Желточный мешок", "Сердцебиение и ЧСС", "Расположение хориона", "Желтое тело",
    "Дополнительные данные", "Заключение", "Рекомендации"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Заключение", callback_data="zakl")],
        [InlineKeyboardButton("🌸 УЗИ для беременных", callback_data="uzi")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите шаблон:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "zakl":
        user_data[chat_id] = {"шаблон": "заключение", "поля": {}, "шаг": 0}
        await query.message.reply_text("Введите ФИО пациента:")
    elif query.data == "uzi":
        user_data[chat_id] = {"шаблон": "узи", "поля": {}, "шаг": 0}
        await query.message.reply_text("Введите ФИО пациента:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if chat_id not in user_data:
        await update.message.reply_text("Пожалуйста, начните с /start 🌸", disable_web_page_preview=True)
        return

    data = user_data[chat_id]
    шаблон = data["шаблон"]
    шаг = data["шаг"]
    поля = FIELDS_ZAKL if шаблон == "заключение" else FIELDS_UZI

    if шаг < len(поля):
        data["поля"][поля[шаг]] = text
        data["шаг"] += 1

    if data["шаг"] < len(поля):
        await update.message.reply_text(f"Введите {поля[data['шаг']]}:", disable_web_page_preview=True)
    else:
        filepath = generate_pdf(data["поля"], "Консультативное заключение" if шаблон == "заключение" else "УЗИ для беременных")
        with open(filepath, "rb") as f:
            await update.message.reply_document(
                document=BytesIO(f.read()),
                filename=os.path.basename(filepath),
                caption="Протокол 🌸"
            )
        del user_data[chat_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
