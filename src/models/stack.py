from sqlalchemy import BigInteger, Column, String, Table, SmallInteger
from sqlalchemy.orm import registry

mapper_registry = registry()


stack_table = Table(
    "stack",
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


class Stack:
    id: int
    name: str
    progress: int


stack_mapper = mapper_registry.map_imperatively(Stack, stack_table)
