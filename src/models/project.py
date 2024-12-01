from sqlalchemy import Column, String, Table, SmallInteger
from sqlalchemy.orm import registry

mapper_registry = registry()


project_table = Table(
    "projects",
    mapper_registry.metadata,
    Column(
        "id",
        SmallInteger,
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("name", String(128), nullable=False),
    Column("description", String(1024), nullable=False),
    Column("url", String(256), nullable=True),
)


class Project:
    id: int
    name: str
    url: str | None


project_mapper = mapper_registry.map_imperatively(Project, project_table)
