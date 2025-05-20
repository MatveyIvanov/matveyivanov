import os

import uvicorn

from config.app import get_fastapi_app

app = get_fastapi_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
