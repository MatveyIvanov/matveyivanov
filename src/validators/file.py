from pathlib import Path
from typing import Any

from validators.interfaces import IValidator


class FileValidator(IValidator):
    def __call__(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        return Path(value).is_file()
