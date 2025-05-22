from pydantic import BaseModel, Field


class ChangelogItem(BaseModel):
    id: str = Field(..., description="Changelog ID")
    title: str = Field(..., description="Changelog title")
    type: str = Field(..., description="Changelog type")
    description: str = Field(..., description="Changelog description")
    version: str = Field(..., description="Changelog version")
    date: str = Field(..., description="Changelog date")


class Changelog(BaseModel):
    updates: list[ChangelogItem]
