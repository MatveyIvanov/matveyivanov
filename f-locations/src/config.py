import os

REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "password")

IPINFO_ACCESS_TOKEN: str = os.environ.get("IPINFO_ACCESS_TOKEN", "")
