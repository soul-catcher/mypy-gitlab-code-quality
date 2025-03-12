import json
import unittest

from mypy_gitlab_code_quality import Severity, parse_issue


class ParsePlainTextTestCase(unittest.TestCase):
    def test_path(self):
        issue = parse_issue("dir/module.py:2: error: Description")
        self.assertEqual("dir/module.py", issue["location"]["path"])

    def test_line_number(self):
        issue = parse_issue("module.py:2: error: Description")
        self.assertEqual(2, issue["location"]["lines"]["begin"])

    def test_fingerprint(self):
        issue = parse_issue("module.py:2: error: Description")
        self.assertEqual("d84c90ce1414af244070c71da60f2388", issue["fingerprint"])

    def test_error_level_error(self):
        issue = parse_issue("module.py:2: error: Description")
        self.assertEqual(Severity.major, issue["severity"])

    def test_error_level_note(self):
        issue = parse_issue("module.py:2: note: Description")
        self.assertEqual(Severity.info, issue["severity"])

    def test_error_level_unknown(self):
        issue = parse_issue("module.py:2: egg: Description")
        self.assertEqual(Severity.unknown, issue["severity"])

    def test_description(self):
        issue = parse_issue("module.py:2: error: Description")
        self.assertEqual("Description", issue["description"])

    def test_description_with_characters(self):
        issue = parse_issue('module.py:2: error: Description "abc" [123] (eee)')
        self.assertEqual('Description "abc" [123] (eee)', issue["description"])

    def test_error_code(self):
        issue = parse_issue("module.py:2: error: Description  [error-code]")
        self.assertEqual("error-code", issue["check_name"])

    def test_column_number(self):
        issue = parse_issue("module.py:2:5: error: Description")
        self.assertEqual(2, issue["location"]["lines"]["begin"])
        self.assertEqual(Severity.major, issue["severity"])

    def test_summary(self):
        issue = parse_issue("Found 5 errors in 1 file (checked 1 source file)")
        self.assertIsNone(issue)


class ParseJsonTestCase(unittest.TestCase):
    def test_path(self):
        issue = parse_issue(
            r"""{
                "file": "dir/module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual("dir/module.py", issue["location"]["path"])

    def test_line_number(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual(2, issue["location"]["lines"]["begin"])

    def test_fingerprint(self):
        fingerprints = set()
        issue_dict = {
            "file": "module.py",
            "line": 2,
            "column": 4,
            "message": "Description",
            "hint": None,
            "code": "error-code",
            "severity": "error",
        }
        issue = parse_issue(json.dumps(issue_dict), fingerprints)
        issue_dict["line"] = 3
        other_issue = parse_issue(json.dumps(issue_dict), fingerprints)
        self.assertEqual("59d5fc1777dba182a0bcac9dc1bd33a6", issue["fingerprint"])
        self.assertEqual("895f1dad0c7bb31d7bb4f792b2b16784", other_issue["fingerprint"])

    def test_error_level_error(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual(Severity.major, issue["severity"])

    def test_error_level_note(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "note"
            }"""
        )
        self.assertEqual(Severity.info, issue["severity"])

    def test_error_level_unknown(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "egg"
            }"""
        )
        self.assertEqual(Severity.unknown, issue["severity"])

    def test_description(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual("Description", issue["description"])

    def test_description_with_characters(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Incompatible (got \"None\", expected \"Object\")",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual(
            'Incompatible (got "None", expected "Object")',
            issue["description"],
        )

    def test_error_code(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": null,
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual("error-code", issue["check_name"])

    def test_hint(self):
        issue = parse_issue(
            r"""{
                "file": "module.py",
                "line": 2,
                "column": 4,
                "message": "Description",
                "hint": "Hint",
                "code": "error-code",
                "severity": "error"
            }"""
        )
        self.assertEqual("Description\nHint", issue["description"])
