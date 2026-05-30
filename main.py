import telebot
import yt_dlp
import os

# ⚠️ ඔයාගේ අලුත් Token එක මෙතනට දෙන්න (කලින් එක Revoke කරන්න)
BOT_TOKEN = "8805960253:AAGIhrdk0mfRt3q-bOgQ7KxBY2ZfkktJnxY" 
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

    # 🍪 මෙන්න මෙතනට තමයි cookies.txt එකතු කරලා තියෙන්නේ
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt',  # <-- Cookies ලබා ගන්නා ෆයිල් එක
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # '192' තත්ත්වයෙන් audio ලබාගනී
        }],
    }

    filename = None # ෆයිල් නාමය මුලින් None ලෙස තබාගන්න

    try:
        # වීඩියෝව ඩවුන්ලෝඩ් කර MP3 බවට හැරවීම
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_filename = ydl.prepare_filename(info)
            filename = os.path.splitext(temp_filename)[0] + '.mp3'

        bot.edit_message_text("✅ Audio downloaded.\n✅ Processing and optimization\n✅ Uploading to Telegram...", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

        # Telegram වෙත යැවීම
        with open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=info.get('title'), performer=info.get('uploader'))
        
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        bot.edit_message_text(f"❌ Error: ඩවුන්ලෝඩ් කිරීමේදී දෝෂයක් ඇතිවිය.\n(විස්තරය: {str(e)[:100]})", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)
                              
    finally:
        # Error එකක් ආවත් නැතත්, අවසානයේදී නිර්මාණය වූ ෆයිල් එක මකා දැමීම 
        if filename and os.path.exists(filename):
            os.remove(filename) 
            print(f"Deleted local file: {filename}")

print("Bot is running...")
bot.infinity_polling()
