from dataclasses import dataclass


@dataclass
class Experience:
    place: str
    from_: str
    to_: str
    description: str
