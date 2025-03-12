from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from functools import reduce
from sys import stdin, stdout
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable


class Severity(str, Enum):
    major = "major"
    info = "info"
    unknown = "unknown"


class GitlabIssueLines(TypedDict):
    begin: int


class GitlabIssueLocation(TypedDict):
    path: str
    lines: GitlabIssueLines


class GitlabIssue(TypedDict):
    description: str
    check_name: str | None
    fingerprint: str
    severity: Severity
    location: GitlabIssueLocation


def parse_issue(line: str, fingerprints: set[str] | None = None) -> GitlabIssue | None:
    if line.startswith("{"):
        try:
            match = json.loads(line)
        except json.JSONDecodeError:
            match = None
        if hint := match.get("hint"):  # attach hint to message
            match["message"] += "\n" + hint
    else:
        match = re.fullmatch(
            r"(?P<file>.+?)"
            r":(?P<line>\d+)(?::\d+)?"  # ignore column number if exists
            r":\s(?P<severity>\w+)"
            r":\s(?P<message>.+?)"
            r"(?:\s\s\[(?P<code>.*)])?",
            line,
        )
    if match is None:
        return None
    error_levels_table = {"error": Severity.major, "note": Severity.info}

    path = match["file"]
    line_number = int(match["line"])
    error_level = match["severity"]
    message = match["message"]
    error_code = match["code"]

    if fingerprints is None:
        fingerprints = set()

    def make_fingerprint(salt: str) -> str:
        fingerprint_text = f"{salt}::{path}::{error_level}::{error_code}::{message}"
        return hashlib.md5(
            fingerprint_text.encode("utf-8"),
            usedforsecurity=False,
        ).hexdigest()

    fingerprint = make_fingerprint("")
    while fingerprint in fingerprints:
        fingerprint = make_fingerprint(fingerprint)
    fingerprints.add(fingerprint)

    return {
        "description": message,
        "check_name": error_code,
        "fingerprint": fingerprint,
        "severity": error_levels_table.get(error_level, Severity.unknown),
        "location": {
            "path": path,
            "lines": {
                "begin": line_number,
            },
        },
    }


def append_or_extend(issues: list[GitlabIssue], new: GitlabIssue) -> list[GitlabIssue]:
    """
    Extend previous issue with description of new one in case of "note" error level.

    It is useful to extend error issues with note issues to prevent inconsistent view
    of code quality widget. For more information see
    https://github.com/soul-catcher/mypy-gitlab-code-quality/pull/3
    """
    is_extend_previous = (
        new["severity"] == Severity.info
        and issues
        and issues[-1]["location"] == new["location"]
    )
    if is_extend_previous:
        issues[-1]["description"] += "\n" + new["description"]
    else:
        issues.append(new)
    return issues


def generate_report(lines: Iterable[str]) -> list[GitlabIssue]:
    fingerprints: set[str] = set()
    issues = filter(None, (parse_issue(line, fingerprints) for line in lines))
    return reduce(append_or_extend, issues, [])


def main() -> None:
    json.dump(generate_report(map(str.rstrip, stdin)), stdout, indent="\t")
