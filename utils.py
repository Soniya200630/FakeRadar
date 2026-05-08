import re
import requests
import aiohttp
import base64
from bs4 import BeautifulSoup


def extract_urls(text: str) -> list:
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


def scrape_article(url: str) -> dict:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = ""
        if soup.find("title"):
            title = soup.find("title").get_text(strip=True)
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        content = ""
        for selector in ["article", "main", ".content", ".post-content", ".entry-content"]:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator=" ", strip=True)
                break

        if not content:
            body = soup.find("body")
            if body:
                content = body.get_text(separator=" ", strip=True)

        content = content[:3000] if len(content) > 3000 else content
        domain = url.split("/")[2] if "/" in url else url

        return {"success": True, "title": title, "content": content, "domain": domain, "url": url}

    except Exception as e:
        return {"success": False, "error": str(e), "url": url, "domain": url.split("/")[2] if "://" in url else url}


async def download_telegram_image(file_path: str, bot_token: str) -> str:
    url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    return base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        print(f"Image download error: {e}")
    return None


def format_score_bar(score: int) -> str:
    filled = round(score / 10)
    empty = 10 - filled
    return "🟩" * filled + "⬜" * empty


def get_score_emoji(score: int) -> str:
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    elif score >= 40:
        return "🟠"
    else:
        return "🔴"


def get_verdict_emoji(verdict: str) -> str:
    mapping = {
        "LIKELY TRUE": "✅",
        "MOSTLY TRUE": "🟢",
        "MIXED": "🟡",
        "MOSTLY FALSE": "🟠",
        "LIKELY FALSE": "❌",
        "UNVERIFIABLE": "❓",
        "LIKELY AUTHENTIC": "✅",
        "PROBABLY AUTHENTIC": "🟢",
        "LIKELY MANIPULATED": "🟠",
        "LIKELY FAKE": "❌",
    }
    return mapping.get(verdict, "❓")


def format_text_result(result: dict) -> str:
    score = result.get("credibility_score", 50)
    verdict = result.get("verdict", "UNVERIFIABLE")
    score_bar = format_score_bar(score)
    score_emoji = get_score_emoji(score)
    verdict_emoji = get_verdict_emoji(verdict)

    msg = "🔍 *FAKЕРАDAR ANALYSIS*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{verdict_emoji} *Verdict:* {verdict}\n"
    msg += f"📊 *Credibility Score:* {score}/100 {score_emoji}\n"
    msg += f"{score_bar}\n\n"
    msg += f"📝 *Summary:*\n{result.get('summary', 'N/A')}\n\n"

    red_flags = result.get("red_flags", [])
    if red_flags:
        msg += "🚩 *Red Flags:*\n"
        for flag in red_flags:
            msg += f"  • {flag}\n"
        msg += "\n"

    positive = result.get("positive_signals", [])
    if positive:
        msg += "✅ *Credibility Signals:*\n"
        for signal in positive:
            msg += f"  • {signal}\n"
        msg += "\n"

    sources = result.get("fact_check_sources", [])
    if sources:
        msg += "🔗 *Verify Here:*\n"
        for source in sources:
            msg += f"  • [{source['name']}]({source['url']}) — {source['relevance']}\n"
        msg += "\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💡 *Recommendation:* {result.get('recommendation', 'Verify before sharing.')}\n\n"
    msg += "_FakeRadar | Fight Misinformation 🛡️_"
    return msg


def format_image_result(result: dict) -> str:
    score = result.get("credibility_score", 50)
    verdict = result.get("verdict", "UNVERIFIABLE")
    score_bar = format_score_bar(score)
    score_emoji = get_score_emoji(score)
    verdict_emoji = get_verdict_emoji(verdict)

    msg = "🖼️ *FAKЕРАDAR IMAGE ANALYSIS*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{verdict_emoji} *Verdict:* {verdict}\n"
    msg += f"📊 *Authenticity Score:* {score}/100 {score_emoji}\n"
    msg += f"{score_bar}\n\n"
    msg += f"🖼️ *Image Shows:*\n{result.get('image_description', 'N/A')}\n\n"

    red_flags = result.get("red_flags", [])
    if red_flags:
        msg += "🚩 *Red Flags:*\n"
        for flag in red_flags:
            msg += f"  • {flag}\n"
        msg += "\n"

    manipulation = result.get("manipulation_indicators", [])
    if manipulation:
        msg += "⚠️ *Manipulation Signs:*\n"
        for indicator in manipulation:
            msg += f"  • {indicator}\n"
        msg += "\n"

    positive = result.get("positive_signals", [])
    if positive:
        msg += "✅ *Authenticity Signals:*\n"
        for signal in positive:
            msg += f"  • {signal}\n"
        msg += "\n"

    sources = result.get("fact_check_sources", [])
    if sources:
        msg += "🔗 *Verify Here:*\n"
        for source in sources:
            msg += f"  • [{source['name']}]({source['url']}) — {source['relevance']}\n"
        msg += "\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💡 *Recommendation:* {result.get('recommendation', 'Verify before sharing.')}\n\n"
    msg += "_FakeRadar | Fight Misinformation 🛡️_"
    return msg