import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

def load_cookies():
    """Railway Variable එකෙන් Cookies File එක හදනවා"""
    cookies = os.getenv("YOUTUBE_COOKIES")
    if cookies:
        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(cookies)
        print("Cookies file created successfully")
    else:
        print("No YOUTUBE_COOKIES found in environment")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive! Link එකක් එවපන් MP3 ගන්න.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("YouTube Link එකක් විතරක් එවපන්.")
        return
    
    msg = await update.message.reply_text("Downloading... ⏳")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'download.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': 'cookies.txt', # Railway Cookies Use කරනවා
        'quiet': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Extension එක mp3 වලට Change කරනවා
            filename = filename.rsplit(".", 1)[0] + ".mp3"
        
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(filename, 'rb'))
        os.remove(filename)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}\n\nCookies Expire වෙලා වෙන්න පුළුවන්. අලුත් Cookies දාපන්.")

if __name__ == '__main__':
    load_cookies() # Bot Start වෙනකොට Cookies File එක හදනවා
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running...")
    app.run_polling()
