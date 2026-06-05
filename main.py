import os
import time
import random
import requests
from flask import Flask
from threading import Thread
from telegram import Bot
import asyncio

# --- تنظیمات وب‌سرور برای زنده نگه داشتن سرویس ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running perfectly!"

def run_web_server():
    # سرویس‌های رایگان مثل Render نیاز دارند یک پورت باز باشد
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- منطق اصلی ربات ---

# این مقادیر را از بخش Environment Variables در مرحله بعد می‌گیریم
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
CONFIG_URL = os.environ.get("CONFIG_URL")

async def send_messages():
    bot = Bot(token=BOT_TOKEN)
    
    print("Bot started...")
    
    while True:
        try:
            print(f"Fetching config from: {CONFIG_URL}")
            response = requests.get(CONFIG_URL, timeout=20)
            response.raise_for_status()
            
            # جدا کردن خطوط و حذف خطوط خالی
            lines = [line.strip() for line in response.text.splitlines() if line.strip()]
            
            if not lines:
                print("Config file is empty. Retrying in 30s...")
                await asyncio.sleep(30)
                continue

            print(f"Found {len(lines)} lines. Starting to send...")

            for line in lines:
                # --- بخش تغییر متن (قابل شخصی‌سازی) ---
                # در اینجا ما فقط یک پیشوند اضافه می‌کنیم، شما می‌توانید هر تغییری بدهید
                modified_text = f"✨ {line} ✨" 
                
                # ارسال پیام
                await bot.send_message(chat_id=CHANNEL_ID, text=modified_text)
                print(f"Sent: {modified_text}")

                # وقفه تصادفی بین 1 تا 5 ثانیه
                wait_time = random.uniform(1, 5)
                await asyncio.sleep(wait_time)

            print("Reached end of file. Restarting loop...")

        except Exception as e:
            print(f"Error occurred: {e}")
            print("Retrying in 30 seconds...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    # اجرای وب‌سرور در یک Thread جداگانه
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

    # اجرای حلقه اصلی ربات با asyncio
    asyncio.run(send_messages())
