from dataclasses import dataclass


@dataclass
class Book:
    name: str
    url: str | None = None
