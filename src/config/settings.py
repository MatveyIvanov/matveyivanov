import logging
import os
from dataclasses import fields
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
else:
    DataclassInstance = None

from dateutil.relativedelta import relativedelta

from schemas.book import Book
from schemas.experience import Experience
from schemas.project import Project
from schemas.python import Python
from schemas.stack import Stack
from validators import (
    validator_int,
    validator_int_boolean,
    validator_template,
    validator_timezone,
    validator_url,
    validator_url_path,
)
from validators.interfaces import IValidator


def load[
    T: str | int | float
](
    key: str,
    default: T,
    *,
    cast_to: type[T] | None = None,
    ensure_not_empty: bool = False,
    validator: IValidator | None = None,
) -> T:
    value = os.environ.get(key, default)
    if not value and ensure_not_empty:
        return default
    casted = value if cast_to is None else cast_to(value)
    if validator and not validator(casted):
        logging.warning(f"Value {casted} is not valid for {key}... using default.")
        return default
    return casted  # type:ignore[return-value]


def load_instances_from_env[
    T: DataclassInstance
](
    type: type[T],
    key: str,
    dict_separator: str = "{dict_separator}",
    value_separator: str = "{value_separator}",
) -> tuple[T, ...]:
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
            for raw_obj in load(key, "").split(dict_separator)
        )
    except TypeError:
        return tuple()


STATIC_URL: str = load(
    "STATIC_URL",
    "/static/",
    ensure_not_empty=True,
    validator=validator_url_path,
)
STATIC_PATH: str = load(
    "STATIC_PATH",
    "static",
    ensure_not_empty=True,
    validator=validator_url_path,
)

REDIS_HOST: str = load("REDIS_HOST", "redis", ensure_not_empty=True)
REDIS_PORT: int = load(
    "REDIS_PORT",
    6379,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
REDIS_PASSWORD: str = load("REDIS_PASSWORD", "password", ensure_not_empty=True)
REDIS_SOCKET_TIMEOUT: int = load(
    "REDIS_SOCKET_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
REDIS_SOCKET_CONNECTION_TIMEOUT: int = load(
    "REDIS_SOCKET_CONNECTION_TIMEOUT",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
REDIS_VISITORS_COUNTER_KEY: str = load(
    "REDIS_VISITORS_COUNTER_KEY",
    "visitors:counter",
    ensure_not_empty=True,
)

SQS_LOCATIONS_ACCESS_KEY = load("SQS_LOCATIONS_ACCESS_KEY", "")
SQS_LOCATIONS_SECRET_KEY = load("SQS_LOCATIONS_SECRET_KEY", "")
SQS_LOCATIONS_ENDPOINT_URL = load("SQS_LOCATIONS_ENDPOINT_URL", "")
SQS_LOCATIONS_QUEUE_URL = load("SQS_LOCATIONS_QUEUE_URL", "")
SQS_LOCATIONS_REGION_NAME = load("SQS_LOCATIONS_REGION_NAME", "")

GITHUB_CREATE_WEBHOOK_TOKEN: str = load("GITHUB_CREATE_WEBHOOK_TOKEN", "")
GITHUB_TAG_PATTERN: str = load(
    "GITHUB_TAG_PATTERN",
    r"^\d+\.\d+\.\d+$",
    ensure_not_empty=True,
)

TIMEZONE: str = load(
    "TIMEZONE",
    "Europe/Moscow",
    ensure_not_empty=True,
    validator=validator_timezone,
)

DEBUG: bool = bool(
    load(
        "DEBUG",
        0,
        cast_to=int,
        ensure_not_empty=True,
        validator=validator_int_boolean,
    )
)
PROD: bool = bool(
    load(
        "PROD",
        1,
        cast_to=int,
        ensure_not_empty=True,
        validator=validator_int_boolean,
    )
)

LOGGING_SENSITIVE_FIELDS = load("LOGGING_SENSITIVE_FIELDS", "").split(",")

ASGI_PORT: int = load(
    "ASGI_PORT",
    8000,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
ABSOLUTE_URL = load(
    "ABSOLUTE_URL",
    f"http://localhost:{ASGI_PORT}",
    ensure_not_empty=True,
    validator=validator_url,
)
ALLOWED_HOSTS = load("ALLOWED_HOSTS", "").split(",")
PROXY_TRUSTED_HOSTS = load(
    "PROXY_TRUSTED_HOSTS",
    "127.0.0.1",
    ensure_not_empty=True,
).split(",")

IMAGE_TAG = load("IMAGE_TAG", "latest", ensure_not_empty=True)

VISITORS_SSE_INTERVAL_SECONDS: int = load(
    "VISITORS_SSE_INTERVAL_SECONDS",
    1,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)

CHANGELOG_SSE_INTERVAL_SECONDS: int = load(
    "CHANGELOG_SSE_INTERVAL_SECONDS",
    1,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
CHANGELOG_BUFFER_NAME: str = load(
    "CHANGELOG_BUFFER_NAME",
    "changelog",
    ensure_not_empty=True,
)
CHANGELOG_BUFFER_MAX_SIZE: int = load(
    "CHANGELOG_BUFFER_MAX_SIZE",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)

LOCATIONS_SSE_INTERVAL_SECONDS: int = load(
    "LOCATIONS_SSE_INTERVAL_SECONDS",
    1,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)
LOCATIONS_BUFFER_NAME: str = load(
    "LOCATIONS_BUFFER_NAME",
    "locations",
    ensure_not_empty=True,
)
LOCATIONS_BUFFER_MAX_SIZE: int = load(
    "LOCATIONS_BUFFER_MAX_SIZE",
    5,
    cast_to=int,
    ensure_not_empty=True,
    validator=validator_int,
)

HTML_FOR_HOME = load(
    "HTML_FOR_HOME",
    "home.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_EXPERIENCE = load(
    "HTML_FOR_EXPERIENCE",
    "experience.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_STACK = load(
    "HTML_FOR_STACK",
    "stack.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_PYTHON = load(
    "HTML_FOR_PYTHON",
    "python.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_BOOKS = load(
    "HTML_FOR_BOOKS",
    "books.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_PROJECTS = load(
    "HTML_FOR_PROJECTS",
    "projects.html",
    ensure_not_empty=True,
    validator=validator_template,
)
HTML_FOR_ERROR = load(
    "HTML_FOR_ERROR",
    "error.html",
    ensure_not_empty=True,
    validator=validator_template,
)

TEMPLATE_CONTEXT_BASE: dict[str, Any] = {
    "IMAGE_TAG": IMAGE_TAG,
    "CHANGELOG_BUFFER_MAX_SIZE": CHANGELOG_BUFFER_MAX_SIZE,
    "LOCATIONS_BUFFER_MAX_SIZE": LOCATIONS_BUFFER_MAX_SIZE,
}

BIRTH_DATE = datetime(2001, 3, 25)

HOME: tuple[str, ...] = tuple(load("HOME", "").split("{newline}")) or (
    "Hello, my name is Matvey Ivanov",
    f"I'm {relativedelta(datetime.now(), BIRTH_DATE).years} y.o.",
    "Currently living in Saint-Petersburg",
    "Full-time middle Python backend developer",
)
EXPERIENCE = load_instances_from_env(Experience, "EXPERIENCE")
STACK = load_instances_from_env(Stack, "STACK")
PYTHON = load_instances_from_env(Python, "PYTHON")
WORK_BOOKS = load_instances_from_env(Book, "WORK_BOOKS")
OFF_WORK_BOOKS = load_instances_from_env(Book, "OFF_WORK_BOOKS")
PROJECTS = load_instances_from_env(Project, "PROJECTS")
