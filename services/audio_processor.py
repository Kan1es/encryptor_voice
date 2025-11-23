"""
Модуль для обработки аудио и видео файлов.
"""
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Класс для обработки аудио и видео файлов."""
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: str, input_format: str = "ogg") -> None:
        """
        Конвертирует аудио файл в формат WAV.
        
        Args:
            input_path: Путь к входному файлу
            output_path: Путь к выходному WAV файлу
            input_format: Формат входного файла (ogg, mp4, mp3 и т.д.)
            
        Raises:
            FileNotFoundError: Если FFmpeg не установлен
            Exception: При ошибке конвертации
        """
        try:
            logger.info(f"Конвертация {input_format.upper()} -> WAV: {input_path}")
            
            # Загружаем аудио в зависимости от формата
            if input_format == "ogg":
                audio = AudioSegment.from_ogg(input_path)
            elif input_format == "mp4":
                audio = AudioSegment.from_file(input_path, format="mp4")
            else:
                audio = AudioSegment.from_file(input_path, format=input_format)
            
            # Экспортируем в WAV
            audio.export(output_path, format="wav")
            logger.info(f"Конвертация завершена: {output_path}")
            
        except FileNotFoundError as e:
            logger.error("FFmpeg не найден!")
            raise FileNotFoundError(
                "FFmpeg не установлен или не найден в PATH. "
                "Установите FFmpeg для работы бота."
            ) from e
        except Exception as e:
            logger.error(f"Ошибка при конвертации файла: {e}")
            raise
    
    @staticmethod
    def extract_audio_from_video(video_path: str, audio_path: str) -> None:
        """
        Извлекает аудио дорожку из видео файла.
        
        Args:
            video_path: Путь к видео файлу
            audio_path: Путь для сохранения аудио
            
        Raises:
            FileNotFoundError: Если FFmpeg не установлен
            Exception: При ошибке извлечения аудио
        """
        try:
            logger.info(f"Извлечение аудио из видео: {video_path}")
            
            # Загружаем видео и извлекаем аудио
            video = AudioSegment.from_file(video_path, format="mp4")
            video.export(audio_path, format="wav")
            
            logger.info(f"Аудио извлечено: {audio_path}")
            
        except FileNotFoundError as e:
            logger.error("FFmpeg не найден!")
            raise FileNotFoundError(
                "FFmpeg не установлен или не найден в PATH. "
                "Установите FFmpeg для работы бота."
            ) from e
        except Exception as e:
            logger.error(f"Ошибка при извлечении аудио из видео: {e}")
            raise
