import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
COOKIES_FILE = "cookies.txt"

def load_cookies():
    """Railway Variable එකෙන් Cookies File එක හදනවා"""
    cookies = os.getenv("YOUTUBE_COOKIES")
    if cookies:
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write(cookies)
        print("Cookies file created successfully.")
    else:
        print("No YOUTUBE_COOKIES found in environment. Running without cookies.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive! Link එකක් එවපන් MP3 ගන්න. 🎧")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong! 🏓")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("YouTube Link එකක් විතරක් එවපන්. ❌")
        return
    
    msg = await update.message.reply_text("Downloading... ⏳")
    filename = None
    
    # ඩවුන්ලෝඩ් Option ටික සකස් කිරීම
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',  # Multi-user crash නොවෙන්න Video ID එක පාවිච්චි කරනවා
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    
    # Cookies ෆයිල් එකක් තිබේ නම් පමණක් එය එක් කරයි
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # yt-dlp මඟින් අවසානයේ ලැබෙන නිවැරදිම mp3 file path එක ලබා ගැනීම
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        
        # Audio එක Telegram එකට Send කිරීම
        await context.bot.send_audio(
            chat_id=update.effective_chat.id, 
            audio=open(filename, 'rb'),
            title=info.get('title', 'Audio'),
            performer=info.get('uploader', 'YouTube')
        )
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}\n\nCookies Expire වෙලා වෙන්න පුළුවන්. නැත්නම් FFmpeg අවුලක්.")
    
    finally:
        # සර්වර් එකේ ඉඩ ඉතිරි කර ගැනීමට ෆයිල් එක අනිවාර්යයෙන්ම මකා දැමීම
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    load_cookies()  # Bot Start වෙනකොට Cookies File එක හදනවා
    
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running successfully...")
    app.run_polling()
