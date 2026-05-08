import subprocess
import sys
import os

print("🚀 Starting FakeRadar on Telegram + WhatsApp...")

base_dir = os.path.dirname(os.path.abspath(__file__))

telegram = subprocess.Popen([sys.executable, os.path.join(base_dir, "bot.py")])
whatsapp = subprocess.Popen([sys.executable, os.path.join(base_dir, "whatsapp_bot.py")])

print("✅ Telegram Bot: Running")
print("✅ WhatsApp Bot: Running")
print("\nPress Ctrl+C to stop\n")

try:
    telegram.wait()
    whatsapp.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all bots...")
    telegram.terminate()
    whatsapp.terminate()