import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from yt_dlp import YoutubeDL
from aiogram import Router, F
import asyncio

# Токен вашего бота
API_TOKEN = ''

# ID разрешенного чата (группы), замените на свой ID
ALLOWED_CHAT_ID = -id  # Убедитесь, что chat_id указан корректно

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Путь для сохранения загруженных видео
DOWNLOAD_PATH = '/tmp/ytbot/'

def download_video(url):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': DOWNLOAD_PATH + '%(title)s.%(ext)s',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@router.message(F.text.contains('https://www.youtube.com/shorts/'))
async def handle_youtube_shorts(message: types.Message):
    if message.chat.id != ALLOWED_CHAT_ID:
        return

    status_message = await message.answer("Downloading")
    try:
        video_path = download_video(message.text)
      
        username = message.from_user.username
        if username:
            caption = f"By @{username}"
        else:
            caption = f"by user_id: {message.from_user.id}"

        video = FSInputFile(video_path)
        await message.answer_video(video, caption=caption)

        await message.delete()

        await status_message.delete()
      
        if os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        await status_message.delete()
        await message.answer(f"err: {str(e)}")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    asyncio.run(main())
