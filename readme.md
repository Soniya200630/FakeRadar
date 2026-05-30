#  FakeRadar
### AI-Powered Misinformation Detector for Telegram

> **"Aaj bhookamp aane wala hai"** — Your family group is full of it. FakeRadar fights back.

FakeRadar is a Telegram bot that instantly fact-checks suspicious news, viral messages, and misinformation using AI and live web search — responding in Hindi or English within seconds.

---

##  The Problem

India is the #1 country for WhatsApp/Telegram misinformation globally. Fake news about health, politics, religion, and finance spreads through family groups every single day. Existing fact-checking websites require users to actively search — too much effort for most people. FakeRadar brings fact-checking **inside the chat**, where misinformation actually lives.

---

##  Features

-  **URL support** — Forward a link, bot fetches and analyzes the article
- **Live web search** — Checks against real-time news and trusted sources
-  **Credibility score** — 0–100 score with clear verdict
-  **Red flag detection** — Highlights specific misleading claims
-  **Hindi + English** — Responds in the language of the input
-  **10-second response** — Fast enough for real conversations

---

##  How It Works

```
User forwards message
        ↓
Bot detects input type (text  / URL )
        ↓
OCR / URL fetch 
        ↓
AI extracts individual checkable claims
        ↓
Live web search across news sites + fact-checkers
        ↓
Cross-check 3+ independent sources
        ↓
Generate credibility score + red flags + verdict
        ↓
Bot replies in Hindi or English with sources
```

---

##  Tech Stack

| Layer | Technology |
|---|---|
| **Bot Framework** | Python Telegram Bot API |
| **AI / LLM** | Groq API|
| **Web Search** | Google Search API / SerpAPI |
| **OCR** | Tesseract / Google Vision API |
| **Language** | Python 3.10+ |
| **Environment** | python-dotenv |
| **Dependencies** | requirements.txt |

---

##  Project Structure

```
fakereader/
├── bot.py              # Telegram bot — handles messages & routing
├── analyzer.py         # Core AI fact-checking logic
├── utils.py            # Helper functions (OCR, search, parsing)
├── test_analyzer.py    # Unit tests for analyzer
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
├── Procfile            # Deployment config
├── .env                # API keys (never commit this)
└── .gitignore          # Excludes .env and cache files
```

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/fakereader.git
cd fakereader
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
SEARCH_API_KEY=your_search_api_key
```

### 4. Run the bot
```bash
python bot.py
```

---

##  Security

- Incoming files are never executed — only text is extracted and analyzed
- File type validation rejects `.exe`, `.apk`, `.sh` and other executables
- All API keys stored in `.env` — never committed to version control
- URL safety check before fetching any external content

---

##  Example Output

```
 FakeRadar Analysis

 Claim: "Aaj bhookamp aane wala hai"

 Credibility Score: 12/100
 Verdict: LIKELY FALSE

 Red Flags:
• No date or location specified
• No seismological agency cited
• Identical message circulated in 2022 and 2024

🔗 Sources:
• National Center for Seismology — no alert issued
• AltNews — previously debunked
• IMD — no earthquake warning active

💡 Tip: Always check ndma.gov.in for official disaster alerts
```

---

## 🚀 Built For

Google Digital Campus Solo Hackathon — solving real-world misinformation at the grassroots level.

---

## 👨‍💻 Author

Built with ❤️ for India's 500M+ messaging app users who deserve the truth.
