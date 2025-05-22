from typing import Dict

from config import settings


def get_config() -> Dict:
    handlers = {
        "uvicorn": {
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
        },
        "console": {
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
        },
    }
    loggers = {
        "uvicorn": {
            "handlers": ["uvicorn"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
        # Не даем стандартному логгеру fastapi работать
        # по пустякам и замедлять работу сервиса
        "uvicorn.access": {
            "handlers": ["uvicorn"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "DEBUG" if settings.DEBUG else "ERROR",
            "propagate": False,
        },
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[{asctime}] [{module}] [{funcName}] [{levelname}] {message}",
                "style": "{",
            },
        },
        "handlers": handlers,
        "loggers": loggers,
    }
