from config import settings


def build_absolute_uri(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return settings.ABSOLUTE_URL + path
