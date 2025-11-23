"""
Telegram бот для транскрипции голосовых сообщений и кружков (video messages).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

from config import Config
from services import FileManager, AudioProcessor, TranscriptionService
import speech_recognition as sr

# Инициализация конфигурации
config = Config.from_env()
config.setup_logging()
config.ensure_temp_dir()

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.bot_token)
dp = Dispatcher()

# Инициализация сервисов
file_manager = FileManager(bot, config.temp_dir)
audio_processor = AudioProcessor()
transcription_service = TranscriptionService(config.recognition_language)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    await message.answer(
        "👋 Привет! Я бесплатный бот-транскрибатор.\n\n"
        "📝 Я умею:\n"
        "• Расшифровывать голосовые сообщения 🎙\n"
        "• Расшифровывать кружки (видео сообщения) 🎥\n\n"
        "Просто отправь мне голосовое сообщение или кружок, "
        "и я превращу его в текст!\n\n"
        "⏱ Обработка может занять несколько секунд."
    )


async def process_media(
    message: types.Message,
    file_id: str,
    media_type: str,
    input_format: str
) -> None:
    """
    Универсальная функция для обработки медиа (голосовые и видео сообщения).
    
    Args:
        message: Сообщение от пользователя
        file_id: ID файла в Telegram
        media_type: Тип медиа ("голосовое сообщение" или "кружок")
        input_format: Формат входного файла ("ogg" или "mp4")
    """
    # Отправляем сообщение о начале обработки
    emoji = "🎙" if media_type == "голосовое сообщение" else "🎥"
    processing_msg = await message.reply(
        f"{emoji} Обрабатываю {media_type}...\n"
        "⏱ Это может занять немного времени"
    )
    
    # Пути к файлам
    input_path = None
    wav_path = None
    
    try:
        # Скачиваем файл
        input_path = await file_manager.download_file(file_id, input_format)
        wav_path = file_manager.get_temp_path(file_id, "wav")
        
        # Конвертируем в WAV
        if input_format == "mp4":
            # Для видео извлекаем аудио
            audio_processor.extract_audio_from_video(input_path, wav_path)
        else:
            # Для аудио просто конвертируем
            audio_processor.convert_to_wav(input_path, wav_path, input_format)
        
        # Распознаем речь
        text = transcription_service.transcribe_audio(wav_path)
        
        # Отправляем результат
        await message.reply(
            f"📝 **Расшифровка {media_type}:**\n\n{text}",
            parse_mode="Markdown"
        )
        logger.info(f"Успешно обработано {media_type} от пользователя {message.from_user.id}")
        
    except sr.UnknownValueError:
        await message.reply(
            "❌ Не удалось распознать речь.\n\n"
            "💡 Попробуйте:\n"
            "• Говорить четче и громче\n"
            "• Уменьшить фоновый шум\n"
            "• Записать сообщение заново"
        )
        logger.warning(f"Речь не распознана для {media_type}")
        
    except sr.RequestError as e:
        await message.reply(
            "❌ Ошибка подключения к сервису распознавания речи Google.\n\n"
            "Пожалуйста, попробуйте позже."
        )
        logger.error(f"Ошибка Google Speech API: {e}")
        
    except FileNotFoundError:
        await message.reply(
            "❌ **Ошибка конфигурации сервера**\n\n"
            "FFmpeg не установлен или не найден.\n"
            "Пожалуйста, свяжитесь с администратором бота."
        )
        logger.error("FFmpeg не найден!")
        
    except Exception as e:
        await message.reply(
            f"❌ Произошла непредвиденная ошибка при обработке {media_type}.\n\n"
            "Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой."
        )
        logger.error(f"Непредвиденная ошибка при обработке {media_type}: {e}", exc_info=True)
        
    finally:
        # Удаляем сообщение о процессе
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id
            )
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение о процессе: {e}")
        
        # Очищаем временные файлы
        file_manager.cleanup(input_path, wav_path)


@dp.message(F.voice)
async def handle_voice_message(message: types.Message):
    """Обработчик голосовых сообщений."""
    logger.info(f"Получено голосовое сообщение от пользователя {message.from_user.id}")
    await process_media(
        message=message,
        file_id=message.voice.file_id,
        media_type="голосовое сообщение",
        input_format="ogg"
    )


@dp.message(F.video_note)
async def handle_video_note(message: types.Message):
    """Обработчик кружков (video messages)."""
    logger.info(f"Получен кружок от пользователя {message.from_user.id}")
    await process_media(
        message=message,
        file_id=message.video_note.file_id,
        media_type="кружок",
        input_format="mp4"
    )


async def main():
    """Главная функция запуска бота."""
    logger.info("Запуск бота...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        print("\n👋 Бот выключен")