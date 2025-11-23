"""
Модуль конфигурации для бота-транскрибатора.
"""
import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """Класс конфигурации приложения."""
    
    # Токен бота
    bot_token: str
    
    # Настройки распознавания речи
    recognition_language: str = "ru-RU"
    
    # Настройки логирования
    log_level: int = logging.INFO
    
    # Директория для временных файлов
    temp_dir: str = "temp"
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Создает конфигурацию из переменных окружения.
        
        Returns:
            Config: Объект конфигурации
            
        Raises:
            ValueError: Если BOT_TOKEN не установлен
        """
        load_dotenv()
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        
        return cls(
            bot_token=bot_token,
            recognition_language=os.getenv("RECOGNITION_LANGUAGE", "ru-RU"),
            log_level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
            temp_dir=os.getenv("TEMP_DIR", "temp")
        )
    
    def setup_logging(self) -> None:
        """Настраивает логирование."""
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def ensure_temp_dir(self) -> None:
        """Создает директорию для временных файлов, если она не существует."""
        os.makedirs(self.temp_dir, exist_ok=True)
