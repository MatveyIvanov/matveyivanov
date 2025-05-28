import uvicorn

from config import settings
from config.app import get_fastapi_app
from utils.exceptions import *  # for exceptions handlers setup  # noqa

app = get_fastapi_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.ASGI_PORT,
        reload=settings.DEBUG,
        proxy_headers=True,
    )
