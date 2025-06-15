from typing import Any

import pytz

from validators.interfaces import IValidator


class TimezoneValidator(IValidator):
    def __call__(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        return value in pytz.all_timezones_set
