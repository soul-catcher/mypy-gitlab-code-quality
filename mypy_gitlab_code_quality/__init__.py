from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from functools import reduce
from sys import stdin, stdout
from typing import Iterable, TypedDict


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


def parse_issue(line: str) -> GitlabIssue | None:
    match = re.fullmatch(
        r"(?P<path>.+?)"
        r":(?P<line_number>\d+)(?::\d+)?"  # ignore column number if exists
        r":\s(?P<error_level>\w+)"
        r":\s(?P<description>.+?)"
        r"(?:\s\s\[(?P<error_code>.*)])?",
        line,
    )
    if match is None:
        return None
    fingerprint = hashlib.md5(line.encode("utf-8")).hexdigest()  # noqa: S324
    error_levels_table = {"error": Severity.major, "note": Severity.info}
    return {
        "description": match["description"],
        "check_name": match["error_code"],
        "fingerprint": fingerprint,
        "severity": error_levels_table.get(match["error_level"], Severity.unknown),
        "location": {
            "path": match["path"],
            "lines": {
                "begin": int(match["line_number"]),
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
    issues = filter(None, map(parse_issue, lines))
    return reduce(append_or_extend, issues, [])


def main() -> None:
    json.dump(generate_report(map(str.rstrip, stdin)), stdout, indent="\t")
