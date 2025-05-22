from dataclasses import dataclass


@dataclass
class IPEvent:
    ip: str
    timestamp: str


@dataclass
class Location:
    name: str
    timestamp: str
