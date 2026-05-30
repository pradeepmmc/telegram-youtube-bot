import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import requests # Thumbnail එක check කිරීමට

# ⚠️ ඔයාගේ අලුත් Token එක මෙතනට දෙන්න (කලින් එක Revoke කරන්න)
BOT_TOKEN = "8759602899:AAHB4en767TTNxuPv71pBhYvrIb6_IIEMyM" 
bot = telebot.TeleBot(BOT_TOKEN)

# ඩවුන්ලෝඩ් බොත්තම් දෙක හදන function එක
def get_download_buttons(video_url):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    # call.data හරහා අපි යවන්නේ (type)|(video_url) කියන එකයි
    markup.add(
        InlineKeyboardButton("⬇️ Download MP3", callback_data=f"audio|{video_url}"),
        InlineKeyboardButton("⬇️ Download MP4", callback_data=f"video|{video_url}")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "ආයුබෝවන්! 👋\n\n"
        "මට YouTube ලින්ක් එකක් එවන්න. මම ඒකේ Audio (MP3) හෝ Video (MP4) "
        "ඩවුන්ලෝඩ් කරලා දෙන්නම්. 🎶📺"
    )
    bot.reply_to(message, welcome_text)

# පියවර 1: ලින්ක් එක ලැබුණු විට - විස්තර සහ බොත්තම් පෙන්වීම
@bot.message_handler(func=lambda message: True)
def process_link(message):
    url = message.text
    
    if "youtu" not in url:
        bot.reply_to(message, "❌ කරුණාකර නිවැරදි YouTube ලින්ක් එකක් ලබා දෙන්න.")
        return

    status_msg = bot.reply_to(message, "🔍 ⏳ වීඩියෝවේ විස්තර සොයමින් පවතී...")

    try:
        # වීඩියෝවේ විස්තර පමණක් ලබා ගැනීම (Download නොකර)
        ydl_opts = {'cookiefile': 'cookies.txt', 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            uploader = info.get('uploader', 'Unknown Channel')
            duration = info.get('duration_string', 'Unknown')
            thumbnail = info.get('thumbnail')

        bot.delete_message(message.chat.id, status_msg.message_id)

        caption = (
            f"🎬 **Title:** {title}\n"
            f"👤 **Channel:** {uploader}\n"
            f"🕒 **Duration:** {duration}\n\n"
            f"ඔයාට ඩවුන්ලෝඩ් කරන්න ඕනේ මොකක්ද? 👇"
        )

        # Thumbnail එක තිබේ නම් එය photo එකක් ලෙස යැවීම
        if thumbnail:
            bot.send_photo(
                message.chat.id, 
                thumbnail, 
                caption=caption, 
                parse_mode='Markdown', 
                reply_markup=get_download_buttons(url)
            )
        else:
            bot.reply_to(message, caption, parse_mode='Markdown', reply_markup=get_download_buttons(url))

    except Exception as e:
        print(f"Info Error: {str(e)}")
        bot.edit_message_text(f"❌ Error: විස්තර ලබා ගැනීමට නොහැකි විය.\n(විස්තරය: {str(e)[:100]})", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

# පියවර 2: බොත්තමක් එබූ විට ක්‍රියාත්මක වන කොටස
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Callback data එක කඩා ගැනීම (type සහ url)
    data_parts = call.data.split('|')
    download_type = data_parts[0]
    url = data_parts[1]

    # බොත්තම එබූ සැණින් "Loading" icon එකක් පෙන්වීමට
    bot.answer_callback_query(call.id, "Starting download...")
    
    # පරණ caption එක වෙනස් කරමු
    bot.edit_message_caption(
        caption="⏳ Request processing...", 
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id
    )

    filename = None
    media_type_str = "Audio" if download_type == "audio" else "Video"
    status_text = f"⏳ {media_type_str} Downloading...\n(This might take a while)"
    
    # status message එකක් යවමු
    status_msg = bot.send_message(call.message.chat.id, status_text)

    # yt-dlp options සකස් කිරීම
    if download_type == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # Video සඳහා (MP4 format එකට ප්‍රමුඛතාවය දෙයි)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': 'cookies.txt',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'media')

        bot.edit_message_text(f"✅ Downloaded.\n✅ Processing...\n✅ Uploading to Telegram...", 
                              chat_id=call.message.chat.id, 
                              message_id=status_msg.message_id)

        # Telegram වෙත යැවීම
        if download_type == "audio":
            # MP3 බවට හැරවූ පසු නම වෙනස් වේ
            filename_mp3 = os.path.splitext(filename)[0] + '.mp3'
            with open(filename_mp3, 'rb') as audio:
                bot.send_audio(call.message.chat.id, audio, title=title, performer=info.get('uploader'))
            filename = filename_mp3 # cleanup සඳහා නම update කිරීම
        else:
import telebot
import yt_dlp
import os

# ඔබේ බොට් ටෝකන් එක මෙතැනට දමන්න
TOKEN = 'ඔබේ_BotFather_Token_එක'
bot = telebot.TeleBot(TOKEN)

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return 'downloaded_video.mp4', info.get('title', 'Video')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "සුබ දවසක්! මට YouTube ලින්ක් එකක් එවන්න, මම ඒක බාගත කර ඔබ වෙත එවන්නම්.")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_youtube_link(message):
    status_msg = bot.reply_to(message, "⏳ කරුණාකර රැඳී සිටින්න, මම වීඩියෝව සකසමින් පවතිමි...")
    filename = None
    
    try:
        url = message.text
        filename, title = download_video(url)
        
        # වීඩියෝ ප්‍රමාණය පරීක්ෂා කිරීම (Telegram API limit: 50MB)
        filesize_mb = os.path.getsize(filename) / (1024 * 1024)
        
        if filesize_mb > 50:
            bot.send_message(message.chat.id, f"⚠️ වීඩියෝව විශාල වැඩියි ({filesize_mb:.1f}MB). ටෙලිග්‍රෑම් සීමාව 50MB කි.")
        else:
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=title)
        
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Download Error: {str(e)}")
        bot.edit_message_text(f"❌ දෝෂයක් ඇතිවිය: {str(e)[:100]}", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)
    finally:
        # cleanup: ෆයිල් එක මකා දැමීම
        if filename and os.path.exists(filename):
            os.remove(filename) 
            print(f"Deleted file: {filename}")

print("Enhanced Bot is running...")
bot.infinity_polling()
