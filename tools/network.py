from __future__ import annotations

from typing import Any
from urllib.request import urlopen

from .base import Tool


class HttpGet(Tool):
    name = "http_get"
    description = "Perform a simple HTTP GET and return text content"

    def run(self, url: str, timeout: int = 10) -> dict[str, Any]:
        with urlopen(url, timeout=timeout) as resp:
            raw = resp.read()
            try:
                text = raw.decode("utf-8")
            except Exception:
                text = raw.decode("latin-1", errors="replace")
        return {"status": resp.status, "content": text}
