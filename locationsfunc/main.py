import json
from typing import Any, Dict

from locationsfunc.src.di import Container
from locationsfunc.src.handle import handle
from locationsfunc.src.types import IPEvent


async def handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    _ = Container()
    for message in event["messages"]:
        message = json.loads(message["details"]["message"]["body"])
        await handle(IPEvent(**message))
