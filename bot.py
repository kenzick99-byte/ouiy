import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import tempfile

# Включи логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
TOKEN = "8380237505:AAHKXYUZ7Q2HKW-2Fd1OWvfOCsYTzvDUevk" 
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '👋 Привет! Просто отправь мне ссылку на видео TikTok, и я скачаю его без водяного знака.'
    )

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    url = message.text.strip()
    
    if not any(url.startswith(prefix) for prefix in [
        'https://www.tiktok.com/', 'https://tiktok.com/', 
        'https://vt.tiktok.com/', 'https://vm.tiktok.com/'
    ]):
        await message.reply_text('❌ Это не ссылка на TikTok. Попробуй ещё раз.')
        return
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'TikTok': {'download_without_watermark': True}},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            if os.path.exists(filename):
                with open(filename, 'rb') as video:
                    await message.reply_video(
                        video=video,
                        caption=f"\n🔗 {url}"
                    )
            else:
                await message.reply_text('Не удалось скачать видео.')
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.reply_text(f'⚠️ Ошибка: {str(e)[:200]}')

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
