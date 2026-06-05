import os
import asyncio
import logging
import httpx
from telegram import Bot
from telegram.error import TelegramError

# --- تنظیمات سیستم Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- دریافت متغیرهای محیطی ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
CONFIG_URL = os.getenv("CONFIG_URL", "").strip()

# --- تنظیمات جایگزینی ---
REPLACEMENT_TEXT = "JasonwolF_shop"

async def fetch_config(url):
    """دریافت محتوای فایل از GitHub"""
    logger.info(f"🔄 Fetching configuration from: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"❌ Error fetching URL: {e}")
            return None

def process_line(line):
    """
    منطق اصلی تغییر متن:
    اگر خط شامل '#' باشد، هر چیزی بعد از آن را حذف کرده و متن جدید را جایگزین می‌کند.
    """
    if "#" in line:
        # بخش قبل از # را جدا می‌کنیم
        base_part = line.split("#")[0].strip()
        # ترکیب بخش اصلی با متن جدید
        # اگر می‌خواهید فاصله هم باشد، می‌توانید: f"{base_part} {REPLACEMENT_TEXT}"
        return f"{base_part} {REPLACEMENT_TEXT}"
    else:
        # اگر خط # نداشت، همان خط را بدون تغییر برمی‌گرداند
        return line.strip()

async def main():
    # ۱. اعتبارسنجی متغیرها
    if not all([BOT_TOKEN, CHANNEL_ID, CONFIG_URL]):
        logger.error("❌ Missing environment variables! Check BOT_TOKEN, CHANNEL_ID, and CONFIG_URL.")
        return

    bot = Bot(token=BOT_TOKEN)

    # ۲. تست اتصال به تلگرام
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot connected as @{me.username}")
    except Exception as e:
        logger.error(f"❌ Invalid Token or Connection Error: {e}")
        return

    # ۳. دریافت فایل از GitHub
    content = await fetch_config(CONFIG_URL)
    if not content:
        logger.error("❌ No content retrieved. Exiting.")
        return

    lines = content.splitlines()
    logger.info(f"📄 Total lines found: {len(lines)}")

    # ۴. پردازش و ارسال خط به خط
    success_count = 0
    error_count = 0

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        # اعمال تغییرات (حذف بعد از # و جایگزینی)
        processed_text = process_line(line)

        try:
            # ارسال پیام (استفاده از HTML برای امنیت بیشتر در کاراکترها)
            await bot.send_message(chat_id=CHANNEL_ID, text=processed_text, parse_mode='HTML')
            success_count += 1
            
            # لاگ کردن هر ۱۰ خط برای جلوگیری از شلوغی بیش از حد لاگ‌ها
            if i % 10 == 0:
                logger.info(f"🚀 Progress: {i}/{len(lines)} lines processed...")

            # وقفه کوتاه برای جلوگیری از اسپم شدن توسط تلگرام (Rate Limit)
            await asyncio.sleep(0.05) 

        except TelegramError as e:
            logger.error(f"❌ Failed to send line {i}: {e}")
            error_count += 1
        except Exception as e:
            logger.error(f"❌ Unexpected error at line {i}: {e}")
            error_count += 1

    logger.info(f"🏁 Finished! Success: {success_count}, Errors: {error_count}")

if __name__ == "__main__":
    asyncio.run(main())
