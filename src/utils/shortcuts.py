from utils.exceptions import Custom404Exception


def get_object_or_404[T](obj: T | None, *, msg: str | None = None) -> T:
    msg = msg or "Not found."
    if obj is None:
        raise Custom404Exception(msg)
    return obj
