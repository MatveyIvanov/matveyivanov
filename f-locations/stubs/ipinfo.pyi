from ipaddress import IPv4Address, IPv6Address
from typing import Any

class Details: ...

class AsyncHandler:
    async def getDetails(
        self,
        ip_address: str | IPv4Address | IPv6Address | None = None,
        timeout: int | None = None,
    ) -> Details: ...

def getHandlerAsync(access_token: str | None = None, **kwargs: Any) -> AsyncHandler: ...
