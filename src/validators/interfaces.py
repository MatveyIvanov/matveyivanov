from typing import Any, Protocol


class IValidator(Protocol):
    def __call__(self, value: Any) -> bool: ...
