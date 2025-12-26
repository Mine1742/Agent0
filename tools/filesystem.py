from __future__ import annotations

from typing import Any
from .base import Tool


class ReadFile(Tool):
    name = "read_file"
    description = "Read text from a file path"

    def run(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()


class SafeWriteFile(Tool):
    name = "write_file"
    description = "Write text to a file path (use carefully)"

    def run(self, path: str, content: str, *, overwrite: bool = False) -> dict[str, Any]:
        # This tool intentionally requires explicit overwrite=True to modify files
        if not overwrite:
            return {"ok": False, "error": "overwrite flag not set"}
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return {"ok": True}
