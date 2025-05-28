import os
from dataclasses import fields
from datetime import datetime
from typing import TYPE_CHECKING, Any, Tuple, TypeVar

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from dateutil.relativedelta import relativedelta

from schemas.book import Book
from schemas.experience import Experience
from schemas.project import Project
from schemas.python import Python
from schemas.stack import Stack

TDataclass = TypeVar("TDataclass", bound=DataclassInstance)

STATIC_URL = os.environ.get("STATIC_URL", "/static/")

REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "password")
REDIS_SOCKET_TIMEOUT: int = int(os.environ.get("REDIS_SOCKET_TIMEOUT", 5))
REDIS_SOCKET_CONNECTION_TIMEOUT: int = int(
    os.environ.get("REDIS_SOCKET_CONNECTION_TIMEOUT", 5)
)
REDIS_VISITORS_COUNTER_KEY: str = os.environ.get(
    "REDIS_VISITORS_COUNTER_KEY",
    "visitors:counter",
)

SQS_LOCATIONS_ACCESS_KEY = os.environ.get("SQS_LOCATIONS_ACCESS_KEY")
SQS_LOCATIONS_SECRET_KEY = os.environ.get("SQS_LOCATIONS_SECRET_KEY")
SQS_LOCATIONS_ENDPOINT_URL = os.environ.get("SQS_LOCATIONS_ENDPOINT_URL")
SQS_LOCATIONS_QUEUE_URL = os.environ.get("SQS_LOCATIONS_QUEUE_URL")
SQS_LOCATIONS_REGION_NAME = os.environ.get("SQS_LOCATIONS_REGION_NAME")

GITHUB_CREATE_WEBHOOK_TOKEN: str = os.environ.get("GITHUB_CREATE_WEBHOOK_TOKEN", "")
GITHUB_TAG_PATTERN: str = os.environ.get("GITHUB_TAG_PATTERN", r"^\d+\.\d+\.\d+$")

TIMEZONE = os.environ.get("TIMEZONE", "Europe/Moscow")

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROD = bool(int(os.environ.get("PROD", 1)))

LOGGING_SENSITIVE_FIELDS = os.environ.get("LOGGING_SENSITIVE_FIELDS", "").split(",")

ASGI_PORT = os.environ.get("ASGI_PORT")
ABSOLUTE_URL = os.environ.get("ABSOLUTE_URL", f"http://localhost:{ASGI_PORT}")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
PROXY_TRUSTED_HOSTS = os.environ.get("PROXY_TRUSTED_HOSTS", "127.0.0.1").split(",")

IMAGE_TAG = os.environ.get("IMAGE_TAG", "latest")

CHANGELOG_SSE_INTERVAL_SECONDS: int = int(
    os.environ.get("CHANGELOG_SSE_INTERVAL_SECONDS", 1)
)
CHANGELOG_VERSION_DEFAULT_DESCRIPTION: str = os.environ.get(
    "CHANGELOG_VERSION_DEFAULT_DESCRIPTION",
    "No description provided.",
)
CHANGELOG_BUFFER_NAME: str = os.environ.get("CHANGELOG_BUFFER_NAME", "changelog")
CHANGELOG_BUFFER_MAX_SIZE: int = int(os.environ.get("CHANGELOG_BUFFER_MAX_SIZE", 5))

LOCATIONS_SSE_INTERVAL_SECONDS: int = int(
    os.environ.get("LOCATIONS_SSE_INTERVAL_SECONDS", 1)
)
LOCATIONS_BUFFER_NAME: str = os.environ.get("LOCATIONS_BUFFER_NAME", "locations")
LOCATIONS_BUFFER_MAX_SIZE: int = int(os.environ.get("LOCATIONS_BUFFER_MAX_SIZE", 5))

HTML_FOR_HOME = os.environ.get("HTML_FOR_HOME", "home.html")
HTML_FOR_EXPERIENCE = os.environ.get("HTML_FOR_EXPERIENCE", "experience.html")
HTML_FOR_STACK = os.environ.get("HTML_FOR_STACK", "stack.html")
HTML_FOR_PYTHON = os.environ.get("HTML_FOR_PYTHON", "python.html")
HTML_FOR_BOOKS = os.environ.get("HTML_FOR_BOOKS", "books.html")
HTML_FOR_PROJECTS = os.environ.get("HTML_FOR_PROJECTS", "projects.html")

TEMPLATE_CONTEXT_BASE: dict[str, Any] = {"IMAGE_TAG": IMAGE_TAG}

BIRTH_DATE = datetime(2001, 3, 25)

HOME: Tuple[str, ...] = tuple(os.environ.get("HOME", "").split("{newline}")) or (
    "Hello, my name is Matvey Ivanov",
    f"I'm {relativedelta(datetime.now(), BIRTH_DATE).years} y.o.",
    "Currently living in Saint-Petersburg",
    "Full-time middle Python backend developer",
)


def load_instances_from_env(
    type: type[TDataclass],
    key: str,
    dict_separator: str = "{dict_separator}",
    value_separator: str = "{value_separator}",
) -> tuple[TDataclass, ...]:
    def parse_value(raw_value: str) -> str | None:
        if raw_value in ("None", "null"):
            return None
        return raw_value

    def load_fields(raw_obj: str) -> dict[str, Any]:
        return {
            field.name: parse_value(value)
            for field, value in zip(fields(type), raw_obj.split(value_separator))
        }

    try:
        return tuple(
            type(**load_fields(raw_obj))
            for raw_obj in os.environ.get(key, "").split(dict_separator)
        )
    except TypeError:
        return tuple()


EXPERIENCE = load_instances_from_env(Experience, "EXPERIENCE")
STACK = load_instances_from_env(Stack, "STACK")
PYTHON = load_instances_from_env(Python, "PYTHON")
WORK_BOOKS = load_instances_from_env(Book, "WORK_BOOKS")
OFF_WORK_BOOKS = load_instances_from_env(Book, "OFF_WORK_BOOKS")
PROJECTS = load_instances_from_env(Project, "PROJECTS")
