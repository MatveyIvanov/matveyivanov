import re
from typing import Any

from validators.interfaces import IValidator

URL_PATTERN = re.compile(
    r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"  # noqa:E501
)
URL_PATH_PATTERN = re.compile(r"^[A-Za-z0-9/]+$")


class RegexValidator(IValidator):
    def __init__(self, pattern: re.Pattern[str]) -> None:
        self.pattern = pattern

    def __call__(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return re.match(self.pattern, value) is not None
