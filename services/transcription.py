"""
Модуль для распознавания речи.
"""
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Класс для распознавания речи из аудио файлов."""
    
    def __init__(self, language: str = "ru-RU"):
        """
        Инициализация сервиса транскрипции.
        
        Args:
            language: Язык для распознавания речи (по умолчанию русский)
        """
        self.language = language
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Распознает речь из WAV файла.
        
        Args:
            audio_path: Путь к WAV файлу
            
        Returns:
            str: Распознанный текст
            
        Raises:
            sr.UnknownValueError: Если речь не распознана
            sr.RequestError: Если проблемы с подключением к API
            Exception: При других ошибках
        """
        try:
            logger.info(f"Начало распознавания речи: {audio_path}")
            
            with sr.AudioFile(audio_path) as source:
                # Записываем аудио данные
                audio_data = self.recognizer.record(source)
                
                # Распознаем с помощью Google Web Speech API
                text = self.recognizer.recognize_google(
                    audio_data, 
                    language=self.language
                )
                
                logger.info(f"Речь успешно распознана: {len(text)} символов")
                return text
                
        except sr.UnknownValueError:
            logger.warning("Google Speech API не смог распознать речь")
            raise
        except sr.RequestError as e:
            logger.error(f"Ошибка подключения к Google Speech API: {e}")
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при распознавании: {e}")
            raise
