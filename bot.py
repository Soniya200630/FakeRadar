import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes,
)
from analyzer import fact_check_text, fact_check_article_url, fact_check_image
from utils import extract_urls, scrape_article, download_telegram_image, format_text_result, format_image_result

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *Welcome to FakeRadar!*\n\n"
        "I detect fake news and misinformation.\n\n"
        "*How to use:*\n"
        "• Forward any suspicious news text\n"
        "• Send a news article URL\n"
        "• Send a suspicious image/screenshot\n\n"
        "📊 Credibility Score • 🚩 Red Flags • 🔗 Sources\n\n"
        "_Fighting misinformation, one fact at a time_ 🔍",
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *FakeRadar Help*\n\n"
        "/start - Welcome message\n"
        "/help - This help message\n\n"
        "*Just send me:*\n"
        "• Any suspicious news text\n"
        "• A URL to a news article\n"
        "• A screenshot or image\n\n"
        "Works with English, Hindi & regional languages!",
        parse_mode="Markdown"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 20:
        await update.message.reply_text("Please send a longer news text or URL to analyze.")
        return

    urls = extract_urls(text)
    thinking_msg = await update.message.reply_text(
        "🔍 *FakeRadar is analyzing...*\n_Please wait 10-15 seconds_",
        parse_mode="Markdown"
    )

    try:
        if urls:
            await thinking_msg.edit_text(f"🌐 Fetching article...\n_Analyzing content_", parse_mode="Markdown")
            scraped = scrape_article(urls[0])
            result = fact_check_article_url(scraped)
        else:
            result = fact_check_text(text)

        formatted = format_text_result(result)
        await thinking_msg.delete()
        await update.message.reply_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Text handler error: {e}")
        await thinking_msg.edit_text("❌ Analysis failed. Please try again.")


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thinking_msg = await update.message.reply_text(
        "🖼️ *Scanning image...*\n_Please wait 10-15 seconds_",
        parse_mode="Markdown"
    )
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_base64 = await download_telegram_image(file.file_path, BOT_TOKEN)

        if not image_base64:
            await thinking_msg.edit_text("❌ Could not download image. Please try again.")
            return

        result = fact_check_image(image_base64, "image/jpeg")
        formatted = format_image_result(result)
        await thinking_msg.delete()
        await update.message.reply_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Image handler error: {e}")
        await thinking_msg.edit_text("❌ Image analysis failed. Please try again.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text("I can only analyze image files.")
        return

    thinking_msg = await update.message.reply_text(
        "🖼️ *Scanning image...*\n_Please wait 10-15 seconds_",
        parse_mode="Markdown"
    )
    try:
        file = await context.bot.get_file(doc.file_id)
        image_base64 = await download_telegram_image(file.file_path, BOT_TOKEN)

        if not image_base64:
            await thinking_msg.edit_text("❌ Could not download image. Please try again.")
            return

        result = fact_check_image(image_base64, doc.mime_type)
        formatted = format_image_result(result)
        await thinking_msg.delete()
        await update.message.reply_text(formatted, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Document handler error: {e}")
        await thinking_msg.edit_text("❌ Image analysis failed. Please try again.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env!")
        return
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in .env!")
        return

    print("🚀 Starting FakeRadar Telegram Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    print("✅ Telegram Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()