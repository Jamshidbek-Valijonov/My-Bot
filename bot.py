import os
import re
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ВСТАВЬ СВОЙ ТОКЕН СЮДА
BOT_TOKEN = "9284292038:AAEyC06_C2tp52pO2ElLwwcCEZOljjtXQeU"
DOWNLOAD_DIR = "./downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

TEXTS = {
    "uz": {
        "welcome": (
            "🔥 <b>Assalomu alaykum, jigarim!</b> 👋\n\n"
            "Men sizga turli platformalardan media yuklab olishda yordam beruvchi botman.\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "📥 <b>VIDEO YUKLASH</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• YouTube (video + shorts)\n"
            "• Instagram (Reels, Post)\n"
            "• TikTok (suv belgisisiz)\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🎵 <b>MUSIQA TOPISH</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• Qo'shiq nomi orqali\n"
            "• Ijrochi ismi orqali\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🚀 <b>QANDAY ISHLATILADI?</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🔗 Havolani yuboring (Video/Audio tanlash uchun).\n"
            "🔍 Yoki qo'shiq nomini yozing (Qidirish uchun)."
        ),
        "choose_lang": "🌐 Iltimos, tilni tanlang:",
        "searching": "🔍 Qidirilmoqda...",
        "search_results": "🔍 Qidiruv natijalari:\n\n",
        "checking": "⏳ Havola tekshirilmoqda...",
        "choose_format": "Formatni tanlang:",
        "downloading": "⏳ Yuklanmoqda va tayyorlanmoqda...",
        "sending_audio": "📤 Audio yuborilmoqda...",
        "sending_video": "📤 Video yuborilmoqda...",
        "error": "❌ Xatolik: ",
        "too_big": "❌ Video juda katta. Telegram limiti 50MB.",
        "btn_video": "📥 Video",
        "btn_audio": "🎧 Audio",
        "btn_dl_video": "📥 Videoni yuklash",
        "error_url": "❌ Xatolik: URL topilmadi"
    },
    "ru": {
        "welcome": (
            "🔥 <b>Привет, бро!</b> 👋\n\n"
            "Я бот, который поможет скачать медиа с разных платформ.\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "📥 <b>СКАЧИВАНИЕ ВИДЕО</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• YouTube (видео + shorts)\n"
            "• Instagram (Reels, Посты)\n"
            "• TikTok (без водяных знаков)\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🎵 <b>ПОИСК МУЗЫКИ</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• По названию песни\n"
            "• По имени исполнителя\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🚀 <b>КАК ЭТО РАБОТАЕТ?</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🔗 Отправь ссылку (чтобы выбрать Видео/Аудио).\n"
            "🔍 Или напиши название песни (для поиска)."
        ),
        "choose_lang": "🌐 Пожалуйста, выберите язык:",
        "searching": "🔍 Ищу...",
        "search_results": "🔍 Результаты поиска:\n\n",
        "checking": "⏳ Проверяю ссылку...",
        "choose_format": "Выбери формат:",
        "downloading": "⏳ Скачиваю и обрабатываю...",
        "sending_audio": "📤 Отправляю аудио...",
        "sending_video": "📤 Отправляю видео...",
        "error": "❌ Ошибка: ",
        "too_big": "❌ Видео слишком большое. Лимит Telegram 50MB.",
        "btn_video": "📥 Видео",
        "btn_audio": "🎧 Аудио",
        "btn_dl_video": "📥 Скачать видео",
        "error_url": "❌ Ошибка: Ссылка не найдена"
    },
    "en": {
        "welcome": (
            "🔥 <b>Hello, bro!</b> 👋\n\n"
            "I am a bot that helps you download media from various platforms.\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "📥 <b>VIDEO DOWNLOAD</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• YouTube (video + shorts)\n"
            "• Instagram (Reels, Posts)\n"
            "• TikTok (no watermark)\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🎵 <b>MUSIC SEARCH</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "• By song name\n"
            "• By artist name\n\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🚀 <b>HOW TO USE?</b>\n"
            "⸻⸻⸻⸻⸻⸻⸻⸻⸻\n"
            "🔗 Send a link (to choose Video/Audio).\n"
            "🔍 Or type a song name (to search)."
        ),
        "choose_lang": "🌐 Please choose a language:",
        "searching": "🔍 Searching...",
        "search_results": "🔍 Search results:\n\n",
        "checking": "⏳ Checking link...",
        "choose_format": "Choose format:",
        "downloading": "⏳ Downloading and processing...",
        "sending_audio": "📤 Sending audio...",
        "sending_video": "📤 Sending video...",
        "error": "❌ Error: ",
        "too_big": "❌ Video is too large. Telegram limit 50MB.",
        "btn_video": "📥 Video",
        "btn_audio": "🎧 Audio",
        "btn_dl_video": "📥 Download video",
        "error_url": "❌ Error: URL not found"
    }
}

def get_text(context, key):
    lang = context.user_data.get('lang', 'uz')
    return TEXTS.get(lang, TEXTS['uz']).get(key, "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(context, "choose_lang"), reply_markup=reply_markup)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split("_")[1]
    context.user_data['lang'] = lang

    image_url = "https://images.unsplash.com/photo-1614149162883-504ce4d13909?q=80&w=1000&auto=format&fit=crop"
    try:
        await query.message.reply_photo(
            photo=image_url, 
            caption=get_text(context, "welcome"), 
            parse_mode='HTML'
        )
        await query.message.delete()
    except Exception:
        await query.message.reply_text(get_text(context, "welcome"), parse_mode='HTML')

async def search_or_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or update.message.caption or ""
    url_match = re.search(r'(https?://[^\s]+)', message_text)
    
    # ИЗМЕНЕНО ЗДЕСЬ (1)
    extractor_opts = {'youtube': {'player_client': ['web_embedded', 'tv', 'web_safari']}}

    if url_match:
        url = url_match.group(1)
        status_msg = await update.message.reply_text(get_text(context, "checking"))

        ydl_opts = {
            'quiet': True, 
            'extract_flat': True, 
            'cookiefile': os.path.abspath('youtube_cookies.txt'), 
            'extractor_args': extractor_opts
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info: info = info['entries'][0]

                title = info.get('title', 'Video')
                thumbnail_url = info.get('thumbnail')
                context.user_data['current_url'] = url

                if "youtube.com" in url or "youtu.be" in url:
                    keyboard = [[
                        InlineKeyboardButton(get_text(context, "btn_video"), callback_data="download_video"),
                        InlineKeyboardButton(get_text(context, "btn_audio"), callback_data="download_audio")
                    ]]
                else:
                    keyboard = [[InlineKeyboardButton(get_text(context, "btn_dl_video"), callback_data="download_video")]]

                reply_markup = InlineKeyboardMarkup(keyboard)
                text = f"🎬 {title}\n\n{get_text(context, 'choose_format')}"

                if thumbnail_url:
                    await update.message.reply_photo(photo=thumbnail_url, caption=text, reply_markup=reply_markup)
                    await status_msg.delete()
                else:
                    await status_msg.edit_text(text, reply_markup=reply_markup)
        except Exception as e:
            await status_msg.edit_text(f"{get_text(context, 'error')}{str(e)}")
        return

    query = message_text
    status_msg = await update.message.reply_text(get_text(context, "searching"))

    ydl_opts = {
        'format': 'bestaudio/best', 
        'quiet': True, 
        'extract_flat': True, 
        'noplaylist': True,
        'extractor_args': extractor_opts
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            entries = [e for e in info['entries'] if e is not None]
            context.user_data['search_results'] = entries

            keyboard, row = [], []
            text = get_text(context, "search_results")
            thumbnail_url = None
            
            for i, entry in enumerate(entries):
                title = entry.get('title', 'Nomsiz')
                duration = entry.get('duration', 0)
                mins, secs = divmod(duration, 60)
                time_str = f"{mins}:{secs:02d}" if duration else ""
                text += f"{i+1}. {title} {time_str}\n"
                
                if i == 0: thumbnail_url = entry.get('thumbnail')
                
                row.append(InlineKeyboardButton(str(i+1), callback_data=f"search_dl_{i}"))
                if len(row) == 5:
                    keyboard.append(row)
                    row = []
            
            if row: keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if thumbnail_url:
                await update.message.reply_photo(photo=thumbnail_url, caption=text, reply_markup=reply_markup)
                await status_msg.delete()
            else:
                await status_msg.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        await status_msg.edit_text(f"{get_text(context, 'error')}{str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action = query.data
    url, is_audio, is_video = None, False, False

    if action.startswith("search_dl_"):
        index = int(action.split("_")[2])
        entries = context.user_data.get('search_results', [])
        if index < len(entries):
            video_id = entries[index].get('id')
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
        is_audio = True
    elif action == "download_audio":
        url = context.user_data.get('current_url')
        is_audio = True
    elif action == "download_video":
        url = context.user_data.get('current_url')
        is_video = True

    if not url:
        await query.message.reply_text(get_text(context, "error_url"))
        return

    status_msg = await query.message.reply_text(get_text(context, "downloading"))

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'ffmpeg_location': '/usr/bin/ffmpeg',
        'noplaylist': True,
        'cookiefile': os.path.abspath('youtube_cookies.txt'), 
        'merge_output_format': 'mp4',
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        # ИЗМЕНЕНО ЗДЕСЬ (3)
        'extractor_args': {'youtube': {'player_client': ['web_embedded', 'tv', 'web_safari']}}
    }

    if is_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'writethumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }, {'key': 'EmbedThumbnail'}],
        })
    elif is_video:
        ydl_opts.update({
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info: info = info['entries'][0]

            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)

            if is_audio:
                final_file = base + ".mp3"
                await status_msg.edit_text(get_text(context, "sending_audio"))
                with open(final_file, 'rb') as f:
                    await query.message.reply_audio(
                        audio=f, 
                        title=info.get('title', 'Unknown'), 
                        performer=info.get('uploader', 'Unknown')
                    )
            elif is_video:
                final_file = base + ".mp4"
                if not os.path.exists(final_file): final_file = filename
                
                file_size = os.path.getsize(final_file) / (1024 * 1024)
                if file_size > 50:
                    await status_msg.edit_text(get_text(context, "too_big"))
                    os.remove(final_file)
                    return

                await status_msg.edit_text(get_text(context, "sending_video"))
                with open(final_file, 'rb') as f:
                    await query.message.reply_video(video=f)

        if os.path.exists(final_file): os.remove(final_file)
        await status_msg.delete()
        await query.message.delete()

    except Exception as e:
        if 'final_file' in locals() and os.path.exists(final_file):
            os.remove(final_file)
        await status_msg.edit_text(f"{get_text(context, 'error')}{str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(MessageHandler((filters.TEXT | filters.Entity("url")) & ~filters.COMMAND, search_or_link))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен...")
    
    web_app = Flask(__name__)

    @web_app.route('/')
    def health_check():
        return "Bot is running!"

    def run_web():
        port = int(os.environ.get("PORT", 10000))
        web_app.run(host='0.0.0.0', port=port)

    Thread(target=run_web).start()
    app.run_polling()

if __name__ == "__main__":
    main()