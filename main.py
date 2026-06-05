import os
import requests
from flask import Flask
from threading import Thread
from telegram import Bot
import asyncio
import random

# تنظیمات سرور (برای زنده ماندن در Render)
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is active and processing lines!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# تنظیمات
BOT_TOKEN = os.environ.get("8946030596:AAE5NEZ7vKqeI1TQrcm9lPXx6C0ni3QM59I")
CHANNEL_ID = os.environ.get("https://t.me/v2ray_free_jasonwolf_shop")
CONFIG_URL = os.environ.get("https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/All_Configs_Sub.txt")

async def process_data():
    bot = Bot(token=BOT_TOKEN)
    print("Starting bot logic...")

    while True: # حلقه اصلی برای بازخوانی کل فایل
        try:
            print(f"Downloading latest config from: {CONFIG_URL}")
            response = requests.get(CONFIG_URL, timeout=30)
            response.raise_for_status()
            lines = [line.strip() for line in response.text.splitlines() if line.strip()]
            
            total_lines = len(lines)
            print(f"Successfully downloaded {total_lines} lines.")

            # شروع پردازش از خط 20 (ایندکس 19)
            # اگر فایل کمتر از 20 خط داشت، از ابتدا شروع کند
            start_index = 19 if total_lines > 20 else 0

            for index in range(start_index, total_lines):
                # شرط توقف پس از 3000 خط (یا پایان فایل)
                if index >= 3000:
                    print("Reached 3000 lines. Breaking to re-download...")
                    break

                line = lines[index]
                current_line_num = index + 1
                
                # اعمال منطق تغییر برند
                if current_line_num > 20 and "#" in line:
                    prefix = line.split("#")[0].strip()
                    final_text = f"{prefix} Jasonwolf_shop"
                else:
                    final_text = line

                # ارسال به تلگرام
                try:
                    await bot.send_message(chat_id=CHANNEL_ID, text=final_text)
                    print(f"Sent line {current_line_num}")
                except Exception as e:
                    print(f"Failed to send line {current_line_num}: {e}")

                # وقفه تصادفی برای جلوگیری از محدودیت تلگرام
                await asyncio.sleep(random.uniform(2, 4))

            print("Cycle completed or 3000 lines reached. Restarting cycle in 60s...")
            await asyncio.sleep(60)

        except Exception as e:
            print(f"Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()
    asyncio.run(process_data())
