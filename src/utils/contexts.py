from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def no_exc() -> Iterator[None]:
    try:
        yield
    except Exception:
        pass
    finally:
        pass
