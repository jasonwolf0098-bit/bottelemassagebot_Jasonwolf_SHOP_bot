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
    """دریافت محتوای فایل از GitHub یا آدرس مستقیم"""
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
    منطق اصلی: حذف متن بعد از # و جایگزینی با JasonwolF_shop
    """
    line = line.strip()
    if not line:
        return None
    
    # اگر خط حاوی # باشد، متن بعد از آن را با مقدار جدید جایگزین می‌کند
    if "#" in line:
        parts = line.split("#", 1)
        base_part = parts[0].strip()
        return f"{base_part}#{REPLACEMENT_TEXT}"
    
    # اگر خط فاقد # باشد، همان‌طور برمی‌گرداند
    return line

async def main():
    # اعتبارسنجی اولیه
    if not all([BOT_TOKEN, CHANNEL_ID, CONFIG_URL]):
        logger.error("❌ Missing environment variables!")
        return

    bot = Bot(token=BOT_TOKEN)

    # دریافت محتوا
    content = await fetch_config(CONFIG_URL)
    if not content:
        return

    lines = content.splitlines()
    logger.info(f"📄 Total lines found: {len(lines)}")

    success_count = 0
    
    for i, line in enumerate(lines, 1):
        processed_text = process_line(line)
        
        # اگر خط معتبر بود ارسال کن
        if processed_text:
            try:
                # استفاده از parse_mode HTML برای جلوگیری از خطا در کاراکترهای خاص
                await bot.send_message(
                    chat_id=CHANNEL_ID, 
                    text=f"<code>{processed_text}</code>", 
                    parse_mode='HTML'
                )
                success_count += 1
                
                if i % 10 == 0:
                    logger.info(f"🚀 Progress: {i}/{len(lines)} lines sent...")

                # وقفه برای جلوگیری از محدودیت تلگرام
                await asyncio.sleep(0.5) 

            except TelegramError as e:
                logger.error(f"❌ Failed to send line {i}: {e}")

    logger.info(f"🏁 Finished! Successfully sent {success_count} lines.")

if __name__ == "__main__":
    asyncio.run(main())
