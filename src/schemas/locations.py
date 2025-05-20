from pydantic import BaseModel


class Location(BaseModel):
    location: str
    timestamp: str


class Locations(BaseModel):
    locations: list[Location]
