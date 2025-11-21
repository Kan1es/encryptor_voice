import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

# Библиотеки для распознавания и конвертации
import speech_recognition as sr
from pydub import AudioSegment

# 1. Настройка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# 2. Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бесплатный бот-транскрибатор. Перешли мне голосовое сообщение, "
        "и я превращу его в текст. (Обработка может занять несколько секунд)"
    )


# 3. Обработчик голосовых сообщений
@dp.message(F.voice)
async def handle_voice_message(message: types.Message):
    processing_msg = await message.reply("🎙 Конвертирую и расшифровываю... (Это может занять немного времени)")

    file_id = message.voice.file_id
    ogg_path = f"{file_id}.ogg"  # Файл, скачанный из Telegram
    wav_path = f"{file_id}.wav"  # Файл, конвертированный для Google API

    try:
        # 3.1. Скачивание файла
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, ogg_path)

        # 3.2. Конвертация OGG -> WAV (Требуется FFmpeg)
        AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")

        # 3.3. Распознавание голоса
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            # Записываем данные с WAV файла
            audio_data = r.record(source)

            # Используем Google Web Speech API с русским языком
        # Это бесплатный метод
        text = r.recognize_google(audio_data, language="ru-RU")

        # Отправляем результат
        await message.reply(f"📝 **Расшифровка:**\n\n{text}")

    except sr.UnknownValueError:
        # Ошибка, если Google не смог понять речь
        await message.reply("Не удалось распознать речь. Попробуйте записать четче.")

    except sr.RequestError:
        # Ошибка, если нет сети или проблемы с API
        await message.reply("Ошибка подключения к сервису распознавания речи Google.")

    except FileNotFoundError:
        # Ошибка, если FFmpeg не установлен или не найден
        await message.reply(
            "❌ **Ошибка конвертации:** Не найдена программа FFmpeg. "
            "Пожалуйста, установите FFmpeg и убедитесь, что он добавлен в PATH."
        )
        logging.error("FFmpeg not found!")

    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")
        await message.reply(f"Произошла непредвиденная ошибка при обработке аудио: {e}")

    finally:
        # Очистка: удаляем временные файлы
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)


# 4. Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")