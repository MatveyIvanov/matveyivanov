import os

REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "password")
REDIS_SOCKET_TIMEOUT: int = int(os.environ.get("REDIS_SOCKET_TIMEOUT", 5))
REDIS_SOCKET_CONNECTION_TIMEOUT: int = int(
    os.environ.get("REDIS_SOCKET_CONNECTION_TIMEOUT", 5)
)

IPINFO_ACCESS_TOKEN: str = os.environ.get("IPINFO_ACCESS_TOKEN", "")
IPINFO_TIMEOUT: int = int(os.environ.get("IPINFO_TIMEOUT", 5))
IPINFO_DEFAULT_CITY: str = os.environ.get("IPINFO_DEFAULT_CITY", "unknown")

LOCATIONS_BUFFER_NAME: str = "locations"
LOCATIONS_BUFFER_MAX_SIZE: int = 5
LOCATIONS_HASHSET_NAME: str = "hashset:locations"
