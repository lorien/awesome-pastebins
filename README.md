
from telegram import Update
   from telegram.ext import Updater, CommandHandler, CallbackContext

   # Anime videolar ro'yxati
   anime_videos = [
       'https://link_to_anime_video_1.mp4',
       'https://link_to_anime_video_2.mp4',
   ]

   def start(update: Update, context: CallbackContext) -> None:
       update.message.reply_text('Salom! Anime videosini ko\'rish uchun /video buyruqinisizlaning.')

   def send_video(update: Update, context: CallbackContext) -> None:
       video_link = anime_videos[0]  # Birinchi videoni yuboradi
       update.message.reply_video(video=video_link)

   def main() -> None:
       updater = Updater("7636027249:AAEehKyW6_kHLkpyXFuZ0RjLQHhJa_k88zc")
       dispatcher = updater.dispatcher

       dispatcher.add_handler(CommandHandler("start", start))
       dispatcher.add_handler(CommandHandler("video", send_video))

       updater.start_polling()
       updater.idle()

   if name == 'main':
       main()
