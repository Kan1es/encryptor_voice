"""
Модуль для управления файлами: скачивание и очистка.
"""
import os
import logging
from typing import Optional
from aiogram import Bot

logger = logging.getLogger(__name__)


class FileManager:
    """Класс для управления временными файлами."""
    
    def __init__(self, bot: Bot, temp_dir: str = "temp"):
        """
        Инициализация менеджера файлов.
        
        Args:
            bot: Экземпляр бота Telegram
            temp_dir: Директория для временных файлов
        """
        self.bot = bot
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def get_temp_path(self, file_id: str, extension: str) -> str:
        """
        Генерирует путь для временного файла.
        
        Args:
            file_id: ID файла в Telegram
            extension: Расширение файла (без точки)
            
        Returns:
            str: Полный путь к временному файлу
        """
        return os.path.join(self.temp_dir, f"{file_id}.{extension}")
    
    async def download_file(self, file_id: str, extension: str) -> str:
        """
        Скачивает файл из Telegram.
        
        Args:
            file_id: ID файла в Telegram
            extension: Расширение файла
            
        Returns:
            str: Путь к скачанному файлу
            
        Raises:
            Exception: При ошибке скачивания
        """
        file_path = self.get_temp_path(file_id, extension)
        
        try:
            file = await self.bot.get_file(file_id)
            await self.bot.download_file(file.file_path, file_path)
            logger.info(f"Файл скачан: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Ошибка при скачивании файла {file_id}: {e}")
            raise
    
    @staticmethod
    def cleanup(*file_paths: str) -> None:
        """
        Удаляет временные файлы.
        
        Args:
            *file_paths: Пути к файлам для удаления
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Удален временный файл: {file_path}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить файл {file_path}: {e}")
