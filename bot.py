import os
import logging
from uuid import uuid4
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    filters
)
from openai import OpenAI

# Load secrets from .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create OpenAI client for Groq
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your MLABEAI AI bot 🤖. Just send me a message! ")

# /caps command
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await update.message.reply_text(text_caps)

# Use Groq to chat (LLaMA3 model)
async def chat_with_groq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.7,
            max_tokens=1000,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"⚠️ Error from Groq: {e}"

    await update.message.reply_text(reply)

# Inline /caps query
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper())
        )
    ]
    await context.bot.answer_inline_query(update.inline_query.id, results)

# Unknown command handler
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Sorry, I didn’t understand that command.")

# Main entry
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("caps", caps))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_groq))
    app.add_handler(InlineQueryHandler(inline_caps))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("MLABEAI Bot is running...")
    app.run_polling()
