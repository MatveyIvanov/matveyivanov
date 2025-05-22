from pydantic import BaseModel


class Location(BaseModel):
    location: str
    timestamp: str


class Locations(BaseModel):
    locations: list[Location]


class IPEvent(BaseModel):
    ip: str
    timestamp: str
