from typing import Any

from fastapi.templating import Jinja2Templates

from utils.uri import build_absolute_uri


def url_for(static_url: str, path: str, *args: Any, **kwargs: Any) -> str:
    return build_absolute_uri(f"{static_url.strip('/')}/{path.strip('/')}")


templates = Jinja2Templates(directory="templates")
templates.env.globals["url_for"] = url_for
