import json
from typing import Any, Dict

from src.di import Container
from src.handle import handle
from src.types import IPEvent


async def handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    _ = Container()
    for message in event["messages"]:
        message = json.loads(message["details"]["message"]["body"])
        await handle(IPEvent(**message))
