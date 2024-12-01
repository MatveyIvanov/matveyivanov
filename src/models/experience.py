from sqlalchemy import Column, String, Table, SmallInteger
from sqlalchemy.orm import registry

mapper_registry = registry()


experience_table = Table(
    "experience",
    mapper_registry.metadata,
    Column(
        "id",
        SmallInteger,
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("place", String(128), nullable=False),
    Column("from_year", SmallInteger, nullable=False),
    Column("to_year", SmallInteger, nullable=False),
    Column("description", String(256), nullable=False),
)


class Experience:
    id: int
    place: str
    from_year: int
    to_year: str
    description: str


experience_mapper = mapper_registry.map_imperatively(Experience, experience_table)
