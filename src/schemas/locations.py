from typing import TypedDict

from pydantic import BaseModel


class LocationDict(TypedDict):
    location: str
    timestamp: str


class Location(BaseModel):
    location: str
    timestamp: str


class Locations(BaseModel):
    locations: list[Location]


class IPEvent(BaseModel):
    ip: str
    timestamp: str
