import os
import base64
import requests
from dotenv import load_dotenv
from whatsapp_chatbot_python import GreenAPIBot, Notification
from analyzer import fact_check_text, fact_check_image
from utils import format_text_result, format_image_result, extract_urls, scrape_article

load_dotenv()

INSTANCE_ID = os.getenv("GREEN_API_INSTANCE")
API_TOKEN = os.getenv("GREEN_API_TOKEN")

bot = GreenAPIBot(INSTANCE_ID, API_TOKEN)


@bot.router.message(type_message="textMessage", regexp=r"(?i)^(/start|hi|hello|helo|hey)$")
def welcome(notification: Notification) -> None:
    notification.answer(
        "🛡️ *Welcome to FakeRadar!*\n\n"
        "I detect fake news & misinformation.\n\n"
        "*How to use:*\n"
        "• Forward any suspicious news text\n"
        "• Send a news article URL\n"
        "• Send a suspicious image\n\n"
        "📊 Score • 🚩 Red Flags • 🔗 Sources\n\n"
        "_Fighting misinformation_ 🔍"
    )


@bot.router.message(type_message="textMessage")
def handle_text(notification: Notification) -> None:
    text = notification.message_text.strip()

    if len(text) < 20:
        notification.answer("Please forward a suspicious news message or send a URL to analyze.")
        return

    notification.answer("🔍 *FakeRadar analyzing...*\n_Please wait 10-15 seconds_")

    try:
        urls = extract_urls(text)
        if urls:
            scraped = scrape_article(urls[0])
            from analyzer import fact_check_article_url
            result = fact_check_article_url(scraped)
        else:
            result = fact_check_text(text)

        notification.answer(format_text_result(result))
    except Exception as e:
        print(f"WhatsApp text error: {e}")
        notification.answer("❌ Analysis failed. Please try again.")


@bot.router.message(type_message="extendedTextMessage")
def handle_forwarded(notification: Notification) -> None:
    try:
        body = notification.event.get("body", {})
        message_data = body.get("messageData", {})
        extended = message_data.get("extendedTextMessageData", {})
        text = extended.get("text", "").strip()

        if not text or len(text) < 20:
            notification.answer("Please forward a complete news article or suspicious message.")
            return

        notification.answer("🔍 *FakeRadar analyzing...*\n_Please wait 10-15 seconds_")
        result = fact_check_text(text)
        notification.answer(format_text_result(result))

    except Exception as e:
        print(f"Forwarded message error: {e}")
        notification.answer("❌ Analysis failed. Please try again.")


@bot.router.message(type_message="imageMessage")
def handle_image(notification: Notification) -> None:
    notification.answer("🖼️ *Scanning image...*\n_Please wait 10-15 seconds_")
    try:
        id_message = notification.event["body"]["idMessage"]
        download_url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/downloadFile/{API_TOKEN}"
        payload = {"idMessage": id_message}
        response = requests.post(download_url, json=payload, timeout=30)

        if response.status_code == 200:
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            result = fact_check_image(image_base64, "image/jpeg")
            notification.answer(format_image_result(result))
        else:
            notification.answer("❌ Could not download image. Please try again.")

    except Exception as e:
        print(f"WhatsApp image error: {e}")
        notification.answer("❌ Image analysis failed. Please try again.")


if __name__ == "__main__":
    if not INSTANCE_ID or not API_TOKEN:
        print("❌ GREEN_API_INSTANCE or GREEN_API_TOKEN not found in .env!")
        exit(1)
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in .env!")
        exit(1)

    print("🚀 Starting FakeRadar WhatsApp Bot...")
    print("✅ WhatsApp Bot is running!")
    bot.run_forever()