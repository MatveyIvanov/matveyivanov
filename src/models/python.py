from sqlalchemy import Column, String, Table, SmallInteger
from sqlalchemy.orm import registry

mapper_registry = registry()


python_table = Table(
    "python",
    mapper_registry.metadata,
    Column(
        "id",
        SmallInteger,
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("name", String(128), nullable=False),
    Column("progress", SmallInteger, nullable=False),
)


class Python:
    id: int
    name: str
    progress: int


python_mapper = mapper_registry.map_imperatively(Python, python_table)
