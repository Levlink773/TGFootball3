import logging
from colorlog import ColoredFormatter

class LoggerConfig:
    @staticmethod
    def setup_logger():
        color_format = (
            '%(log_color)s%(asctime)s | %(levelname)-5s | %(filename)-14s | %(funcName)-10s | %(message)s%(reset)s'
        )

        formatter = ColoredFormatter(
            fmt=color_format,
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={  
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        # Потоковый обработчик (для вывода в консоль)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)  # В консоли показывать все сообщения с уровня INFO
        handler.setFormatter(formatter)

        # Файловый обработчик (для записи в файл)
        file_handler = logging.FileHandler('error_logs.log', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)  # В файл записывать только сообщения с уровня ERROR и выше
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%Y-%m-%d %H:%M:%S'))

        # Настройка логгера
        logging.basicConfig(level=logging.INFO, handlers=[handler, file_handler], force=True)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
    
LoggerConfig.setup_logger()
logger = LoggerConfig.get_logger(__name__)
