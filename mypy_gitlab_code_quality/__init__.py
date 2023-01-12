from __future__ import annotations

import json
import re
from base64 import b64encode
from collections.abc import Hashable, Sequence
from sys import byteorder, hash_info, stdin
from typing import TextIO

SEVERITY = {
    "note": "info",
    "error": "major",
}


def get_hash(tpl: Sequence[Hashable]) -> str:
    return b64encode(
        hash(tpl).to_bytes(hash_info.width // 8, byteorder, signed=True)
    ).decode()


def is_info_to_previous_issue(
    issues: list[dict], severity: str, lineNumber: int
) -> bool:
    return issues and (severity == "info") and (
        issues[-1]["location"]["lines"]["begin"] == lineNumber
    )


def append_line_to_issues(
    issues: list[dict],
    fingerprint: str,
    severity: str,
    lineNumber: int,
    description: str,
    path: str,
) -> None:
    if is_info_to_previous_issue(issues, severity, lineNumber):
        issues[-1]["description"] += f"\n{description}"
    else:
        issues.append(
            {
                "description": description,
                "fingerprint": fingerprint,
                "severity": severity,
                "location": {
                    "path": path,
                    "lines": {
                        "begin": lineNumber,
                    },
                },
            }
        )


def parse_lines(lines: TextIO) -> list[dict]:
    issues: list[dict] = []
    for line in lines:
        line = line.rstrip("\n")
        match = re.fullmatch(
            r"(?P<path>.+?)"
            r":(?P<line>\d+)"
            r":(?:\d+:)?\s(?P<error_level>\w+)"
            r":\s(?P<description>.+)",
            line,
        )
        if match is None:
            continue
        fingerprint: str = get_hash(match.groups())
        severity: str = SEVERITY.get(match["error_level"], "unknown")
        lineNumber: int = int(match["line"])
        description: str = match["description"]
        path: str = match["path"]
        append_line_to_issues(
            issues, fingerprint, severity, lineNumber, description, path
        )
    return issues


def main() -> None:
    print(
        json.dumps(
            parse_lines(stdin),
            indent="\t",
        )
    )
