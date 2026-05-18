import yt_dlp
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import edge_tts  # Microsoft Voice පැකේජ් එක

# Railway Environment Variables වලින් Token එක ලබා ගැනීම
# (Railway එකේ BOT_TOKEN කියන තැනට ඔයාගේ Token එක ඇතුලත් කරන්න)
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
    await update.message.reply_text(
        "ආයුබෝවන්! මම සූදානම්. 🎶\n\n"
        "👉 ඕනෑම YouTube Link එකක් එවන්න, මම ඒකේ MP3 එක ඩවුන්ලෝඩ් කරලා දෙන්නම්.\n"
        "👉 සිංහලෙන් Voice එකක් හදාගන්න /speak ලියා ඉඩක් තබා වචන ටයිප් කරන්න.\n"
        "   (උදා: /speak කොහොමද යාලුවනේ)"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong! 🏓 බොට් වැඩ කරනවා...")

# --- Microsoft Edge TTS Function එක (සිංහල කටහඬ) ---
async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    
    if not text:
        await update.message.reply_text("කරුණාකර /speak එකට පස්සේ මොනවා හරි ටයිප් කරන්න.\nඋදා: /speak කොහොමද ඔයාට")
        return
    
    msg = await update.message.reply_text("🎙️ Voice එක සකසමින් පවතී...")
    filename = "voice.mp3"
    
    try:
        # සිංහල ගැහැණු කටහඬ: 'si-LK-ThiliniNeural'
        # සිංහල පිරිමි කටහඬ: 'si-LK-SameeraNeural'
        voice = 'si-LK-ThiliniNeural' 
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
        
        # Voice එකක් ලෙස ටෙලිග්‍රෑම් එකට යැවීම
        with open(filename, 'rb') as voice_file:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# --- YouTube MP3 Downloader Function එක ---
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # YouTube ලින්ක් එකක්දැයි පරීක්ෂා කිරීම
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("කරුණාකර නිවැරදි YouTube ලින්ක් එකක් විතරක් එවන්න. ❌")
        return
    
    # ඡායාරූපයේ තිබූ ආකාරයට ස්ටෙප් බයි ස්ටෙප් මැසේජ් එක සැකසීම
    msg = await update.message.reply_text(
        "👩‍⚕️ Request processing:\n\n"
        "⏳ Downloading audio..."
    )
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
    
    # Cookies ෆයිල් එක තිබේ නම් එය සම්බන්ධ කිරීම
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
    
    try:
        # 1. ඩවුන්ලෝඩ් වීම
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        
        # මැසේජ් එක අප්ඩේට් කිරීම
        await msg.edit_text(
            "👩‍⚕️ Request processing:\n\n"
            "✅ Downloading audio\n"
            "⏳ Processing and optimization..."
        )
        
        # ටෙලිග්‍රෑම් එකට අප්ලෝඩ් වන බව පෙන්වීම
        await msg.edit_text(
            "👩‍⚕️ Request processing:\n\n"
            "✅ Downloading audio\n"
            "✅ Processing and optimization\n"
            "⏳ Uploading to Telegram..."
        )
        
        # Audio ෆයිල් එක යැවීම
        with open(filename, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id, 
                audio=audio_file,
                title=info.get('title', 'Audio'),
                performer=info.get('uploader', 'YouTube')
            )
        
        # සාර්ථකව අවසන් වූ පසු Progress මැසේජ් එක මකා දැමීම
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(
            f"❌ Error: {str(e)[:100]}\n\n"
            "Cookies Expire වෙලා වෙන්න පුළුවන්. නැත්නම් FFmpeg අවුලක්."
        )
    
    finally:
        # සර්වර් එකේ ඉඩ ඉතුරු කරගැනීමට ෆයිල් එක මැකීම
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    load_cookies()  
    
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers ඇතුලත් කිරීම
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("speak", speak)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    
    print("Bot is running successfully...")
    app.run_polling()
