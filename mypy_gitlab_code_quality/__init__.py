from __future__ import annotations

import json
import re
from base64 import b64encode
from collections.abc import Hashable, Sequence
from sys import byteorder, hash_info, stdin

SEVERITY = {
    "note": "info",
    "error": "major",
}


def get_hash(tpl: Sequence[Hashable]) -> str:
    return b64encode(hash(tpl).to_bytes(hash_info.width // 8, byteorder, signed=True)).decode()


def parse_line(line: str) -> dict[str, str | dict[str, str | dict[str, int]]] | None:
    match = re.fullmatch(r"(?P<path>.+?):(?P<line>\d+):(?:\d+:)?\s(?P<error_level>\w+):\s(?P<description>.+)", line)
    if match is None:
        return None
    return {
        "description": match["description"],
        "fingerprint": get_hash(match.groups()),
        "severity": SEVERITY.get(match["error_level"], "unknown"),
        "location": {
            "path": match["path"],
            "lines": {
                "begin": int(match["line"]),
            },
        },
    }


def main() -> None:
    print(json.dumps(list(filter(None, (parse_line(line.rstrip("\n")) for line in stdin))), indent="\t"))
