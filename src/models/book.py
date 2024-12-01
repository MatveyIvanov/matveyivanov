from sqlalchemy import Column, String, Table, SmallInteger
from sqlalchemy.orm import registry

mapper_registry = registry()


book_table = Table(
    "books",
    mapper_registry.metadata,
    Column(
        "id",
        SmallInteger,
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("name", String(128), nullable=False),
    Column("url", String(256), nullable=True),
)


class Book:
    id: int
    name: str
    url: str | None


book_mapper = mapper_registry.map_imperatively(Book, book_table)
