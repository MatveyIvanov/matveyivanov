from validators.file import TemplateValidator
from validators.int import IntBooleanValidator, IntValidator
from validators.regex import URL_PATH_PATTERN, URL_PATTERN, RegexValidator
from validators.timezone import TimezoneValidator

__all__ = [
    "validator_int",
    "validator_int_boolean",
    "validator_url",
    "validator_url_path",
    "validator_timezone",
    "validator_template",
]

validator_int = IntValidator()
validator_int_boolean = IntBooleanValidator()
validator_url = RegexValidator(URL_PATTERN)
validator_url_path = RegexValidator(URL_PATH_PATTERN)
validator_timezone = TimezoneValidator()
validator_template = TemplateValidator()
