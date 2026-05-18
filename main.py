import telebot
import yt_dlp
import os

# ඔයාගේ Telegram Bot Token එක කෙලින්ම මෙතනට නිවැරදිව ඇතුලත් කර ඇත
BOT_TOKEN = "8814569576:AAEP-4qn64z8OramKli2x063OOwbZq894Rk"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! මට YouTube ලින්ක් එකක් එවන්න, මම ඒකේ Audio එක ඩවුන්ලෝඩ් කරලා දෙන්නම්. 🎶")

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    url = message.text
    
    if "youtu" not in url:
        bot.reply_to(message, "කරුණාකර නිවැරදි YouTube ලින්ක් එකක් ලබා දෙන්න.")
        return

    status_msg = bot.reply_to(message, "⏳ Request processing:\n\n✅ Downloading audio...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.splitext(filename)[0] + '.mp3'

        bot.edit_message_text("✅ Audio downloaded.\n✅ Processing and optimization\n✅ Uploading to Telegram...", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'), performer=info.get('uploader'))
        
        if os.path.exists(filename):
            os.remove(filename) 
        
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        bot.edit_message_text(f"❌ Error: ඩවුන්ලෝඩ් කිරීමේදී දෝෂයක් ඇතිවිය.\n(විස්තරය: {str(e)[:100]})", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

print("Bot is running...")
bot.infinity_polling()
