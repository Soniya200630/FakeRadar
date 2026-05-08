import os
from dotenv import load_dotenv
from analyzer import fact_check_text, fact_check_image
from utils import format_text_result, format_image_result
import base64, sys

load_dotenv()

def test_fake_news():
    print("=" * 60)
    print("TEST 1: Fake News")
    print("=" * 60)
    text = """BREAKING: Scientists confirm 5G towers are spreading COVID-19!
Government hiding this truth. Bill Gates installed microchips in vaccines.
Share before it gets deleted! The mainstream media won't show you this!"""
    result = fact_check_text(text)
    print(format_text_result(result))

def test_real_news():
    print("\n" + "=" * 60)
    print("TEST 2: Real News")
    print("=" * 60)
    text = """India's GDP grew by 7.2% last quarter according to the National
Statistical Office report. The Finance Ministry confirmed the figures,
attributing growth to strong manufacturing and services sectors."""
    result = fact_check_text(text)
    print(format_text_result(result))

def test_hindi():
    print("\n" + "=" * 60)
    print("TEST 3: Hindi Fake News")
    print("=" * 60)
    text = """सावधान! सरकार ने कल से सभी बैंक खाते बंद करने का फैसला किया है।
अभी अपना सारा पैसा निकाल लें! इसे सभी को भेजें।"""
    result = fact_check_text(text)
    print(format_text_result(result))

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in .env!")
        exit(1)
    print("🛡️ FakeRadar Tests (Groq API)\n")
    test_fake_news()
    test_real_news()
    test_hindi()
    print("\n✅ All tests done!")