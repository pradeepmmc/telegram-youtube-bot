import telebot
import yt_dlp
import os

# ඔබේ Telegram Bot Token එක මෙතනට ඇතුලත් කරන්න
BOT_TOKEN = "8814569576:AAEP-4qn64z8OramKIi2x063OOwbZq894Rk"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! මට YouTube ලින්ක් එකක් එවන්න, මම ඒකේ Audio එක ඩවුන්ලෝඩ් කරලා දෙන්නම්. 🎶")

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    url = message.text
    
    # YouTube ලින්ක් එකක්දැයි මූලිකව පරීක්ෂා කිරීම
    if "youtu" not in url:
        bot.reply_to(message, "කරුණාකර නිවැරදි YouTube ලින්ක් එකක් ලබා දෙන්න.")
        return

    # පණිවිඩයක් යැවීම (Request processing...)
    status_msg = bot.reply_to(message, "⏳ Request processing:\n\n✅ Downloading audio...")

    # yt-dlp සඳහා සැකසුම් (mp3 ලෙස ලබා ගැනීම)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # කලින් තිබුණු cookies ප්‍රශ්නය මගහැරීමට ඔබගේ cookies.txt ෆයිල් එක මෙතනට සම්බන්ධ කළ හැක
        # 'cookiefile': 'cookies.txt', 
    }

    try:
        # Audio එක ඩවුන්ලෝඩ් කිරීම
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # FFmpeg මගින් file extension එක .mp3 බවට පත් කරන බැවින් නම යාවත්කාලීන කිරීම
            filename = os.path.splitext(filename)[0] + '.mp3'

        # Telegram එකට අප්ලෝඩ් කරන බව දැනුම් දීම
        bot.edit_message_text("✅ Audio downloaded.\n✅ Processing and optimization\n✅ Uploading to Telegram...", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

        # Audio ෆයිල් එක Telegram හරහා යැවීම
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'), performer=info.get('uploader'))
        
        # යැව්වට පස්සේ සර්වර් එකේ ඉඩ ඉතුරු කරගන්න ෆයිල් එක මකා දැමීම
        os.remove(filename) 
        
        # Status මැසේජ් එක මකා දැමීම
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: ඩවුන්ලෝඩ් කිරීමේදී දෝෂයක් ඇතිවිය.\n(විස්තරය: {str(e)[:100]})", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

print("Bot is running...")
# බොට් නතර නොවී වැඩ කිරීම සඳහා
bot.infinity_polling()
