import logging
import sys
from pprint import pformat

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from app.settings import BASE_DIR, LOGURU_CONF


class InterceptHandler(logging.Handler):
    """
    Handler для перехвата логов стандартного logging и перенаправления в loguru.
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Кастомный формат для loguru логов.
    """

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def init_logging():
    """
    Инициализация глобального логирования через loguru.
    """

    # Отключаем стандартные обработчики для логов uvicorn.
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    # Устанавливаем стандартный формат для loguru.
    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]

    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.INFO, "format": format_record}]
    )
    logger.add(
        BASE_DIR / "logs" / "info.log",
        level="INFO",
        **LOGURU_CONF,
    )
    logger.add(
        BASE_DIR / "logs" / "warning.log",
        level="WARNING",
        **LOGURU_CONF,
    )
    logger.add(
        BASE_DIR / "logs" / "error.log",
        level="ERROR",
        **LOGURU_CONF,
    )
