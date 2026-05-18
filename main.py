import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import edge_tts # අලුත් Microsoft Voice පැකේජ් එක

TOKEN = os.getenv("BOT_TOKEN")
COOKIES_FILE = "cookies.txt"

def load_cookies():
    cookies = os.getenv("YOUTUBE_COOKIES")
    if cookies:
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write(cookies)
        print("Cookies file created successfully from environment variable.")
    else:
        print("No YOUTUBE_COOKIES found in environment. Bot will use the manually uploaded cookies.txt file.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive! \n👉 Link එකක් එවපන් MP3 ගන්න.\n👉 /speak කියලා ටයිප් කරලා වචන දීලා Voice එකක් ගන්න. 🎧")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong! 🏓")

# --- අලුත් Microsoft Edge TTS Function එක ---
async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    
    if not text:
        await update.message.reply_text("කරුණාකර /speak එකට පස්සේ මොනවා හරි ටයිප් කරන්න.\nඋදා: /speak කොහොමද ඔයාට")
        return
    
    msg = await update.message.reply_text("Voice එක හදනවා... 🎙️")
    filename = "voice.mp3"
    
    try:
        # මෙතනින් ඔයාට කටහඬ මාරු කරන්න පුළුවන්:
        # පිරිමි කටහඬට ඕන නම්: 'si-LK-SameeraNeural'
        # ගැහැණු කටහඬට ඕන නම්: 'si-LK-ThiliniNeural'
        
        voice = 'si-LK-ThiliniNeural' 
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(filename, 'rb'))
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)
# ------------------------------------------

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("YouTube Link එකක් විතරක් එවපන්. ❌")
        return
    
    msg = await update.message.reply_text("Downloading... ⏳")
    filename = None
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',  
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    
    # Cookies ෆයිල් එක භාවිතා කිරීම
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        
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
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    load_cookies()  
    
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("speak", speak)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running successfully...")
    app.run_polling()
