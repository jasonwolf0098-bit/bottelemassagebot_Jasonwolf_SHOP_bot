import os
import time
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Bot

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
CONFIG_URL = os.environ.get("CONFIG_URL")

bot = Bot(token=BOT_TOKEN)


@app.route("/")
def home():
    return "Bot is running"


def fetch_lines():
    r = requests.get(CONFIG_URL, timeout=20)
    r.raise_for_status()
    return [line.strip() for line in r.text.splitlines() if line.strip()]


def modify_line(line):
    # اینجا هر تغییری که بخواهی روی متن اعمال می‌شود
    return f"📌 {line}"


def send_loop():
    while True:
        try:
            lines = fetch_lines()
            for line in lines:
                text = modify_line(line)
                bot.send_message(chat_id=CHANNEL_ID, text=text)
                time.sleep(random.uniform(1, 5))
        except Exception as e:
            print("Error:", e)
            time.sleep(10)


def run_sender():
    t = Thread(target=send_loop, daemon=True)
    t.start()


if __name__ == "__main__":
    run_sender()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

