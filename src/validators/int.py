from typing import Any

from validators.interfaces import IValidator


class IntValidator(IValidator):
    def __call__(self, value: Any) -> bool:
        if isinstance(value, int):
            return True
        try:
            int(value)
        except Exception:
            return False
        else:
            return True


class IntBooleanValidator(IValidator):
    def __call__(self, value: Any) -> bool:
        if not isinstance(value, int):
            return False

        return value in (0, 1)
