import telebot
import yt_dlp
import os

# මෙතැනට ඔබේ අලුත් ටෝකනය දාන්න
TOKEN = '8759602899:AAHB4en767TTNxuPv71pBhYvrIb6_IIEMyM' 
bot = telebot.TeleBot(TOKEN)

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return 'downloaded_video.mp4', info.get('title', 'Video')

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_youtube_link(message):
    status_msg = bot.reply_to(message, "⏳ බාගත කරමින් පවතිනවා, මොහොතක් රැඳී සිටින්න...")
    filename = None
    
    try:
        filename, title = download_video(message.text)
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=title)
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ දෝෂයක්: {str(e)[:50]}", chat_id=message.chat.id, message_id=status_msg.message_id)
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

print("Bot is running...")
bot.infinity_polling()
