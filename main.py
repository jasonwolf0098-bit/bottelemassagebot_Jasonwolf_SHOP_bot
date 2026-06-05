import os
import asyncio
import logging
import random
import httpx
from flask import Flask
from threading import Thread
from telegram import Bot
from telegram.error import InvalidToken

# --- تنظیمات لاگینگ برای مشاهده بهتر در Railway ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- دریافت متغیرهای محیطی ---
# استفاده از .strip() برای حذف فاصله‌های احتمالی در کپی کردن
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
CONFIG_URL = os.getenv("CONFIG_URL", "").strip()

# --- تنظیمات Flask برای جلوگیری از خوابیدن سرویس در Railway ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    # اجرای Flask روی پورت 8080 (پورت استاندارد Railway)
    app.run(host='0.0.0.0', port=8080)

# --- تابع اصلی پردازش ---
async def process_data():
    # ۱. بررسی وجود متغیرها
    if not BOT_TOKEN:
        logger.error("❌ ERROR: BOT_TOKEN is missing in Environment Variables!")
        return
    if not CHANNEL_ID:
        logger.error("❌ ERROR: CHANNEL_ID is missing in Environment Variables!")
        return
    if not CONFIG_URL:
        logger.error("❌ ERROR: CONFIG_URL is missing in Environment Variables!")
        return

    # چاپ وضعیت برای اطمینان (در لاگ‌ها نمایش داده می‌شود)
    logger.info(f"✅ Environment Variables loaded. (Token starts with: {BOT_TOKEN[:10]}...)")
    logger.info(f"✅ Target Channel ID: {CHANNEL_ID}")

    try:
        bot = Bot(token=BOT_TOKEN)
        # یک تست کوچک برای اطمینان از صحت توکن
        await bot.get_me()
        logger.info("✅ Bot connection successful!")
    except InvalidToken:
        logger.error("❌ ERROR: The BOT_TOKEN is invalid! Please check your token in Railway Variables.")
        return
    except Exception as e:
        logger.error(f"❌ ERROR: Could not connect to Telegram: {e}")
        return

    async with httpx.AsyncClient() as client:
        while True:
            try:
                logger.info(f"🔄 Fetching configuration from: {CONFIG_URL}")
                response = await client.get(CONFIG_URL)
                
                if response.status_code != 200:
                    logger.error(f"⚠️ Failed to fetch config. Status: {response.status_code}")
                    await asyncio.sleep(30)
                    continue

                content = response.text
                lines = content.splitlines()
                logger.info(f"📄 Content fetched. Total lines: {len(lines)}")

                for i, line in enumerate(lines):
                    # شروع پردازش از خط ۲۰ (اندیس ۱۹ در پایتون)
                    if i >= 19:
                        # حذف متن بعد از # و جایگزینی با نام فروشگاه
                        processed_line = line.split('#')[0].strip() + " | Jasonwolf_shop"
                        
                        try:
                            await bot.send_message(chat_id=CHANNEL_ID, text=processed_line)
                            logger.info(f"📤 Sent line {i+1}")
                            
                            # ایجاد تاخیر تصادفی بین ۲ تا ۴ ثانیه برای جلوگیری از اسپم و بلاک شدن
                            delay = random.uniform(2, 4)
                            await asyncio.sleep(delay)
                        except Exception as msg:
                            logger.error(f"❌ Failed to send line {i+1}: {msg}")
                            await asyncio.sleep(5)

                logger.info("🏁 Reached end of file. Restarting loop in 30 seconds...")
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"🔥 Unexpected error in main loop: {e}")
                await asyncio.sleep(30)

# --- نقطه ورود برنامه ---
if __name__ == "__main__":
    # اجرای Flask در یک Thread جداگانه
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # اجرای حلقه اصلی ربات
    try:
        asyncio.run(process_data())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user.")
