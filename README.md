![Gitlab-CI](https://img.shields.io/badge/GitLab_CI-indigo?logo=gitlab)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-gitlab-code-quality)
[![PyPI](https://img.shields.io/pypi/v/mypy-gitlab-code-quality)](https://pypi.org/project/mypy-gitlab-code-quality/)
[![Downloads](https://static.pepy.tech/badge/mypy-gitlab-code-quality/month)](https://pepy.tech/project/mypy-gitlab-code-quality)
![PyPI - License](https://img.shields.io/pypi/l/mypy-gitlab-code-quality)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# mypy-gitlab-code-quality
Simple script to generate [gitlab code quality report](https://docs.gitlab.com/ci/testing/code_quality/)
from output of [mypy](http://www.mypy-lang.org/).

Example gitlab codequality widget from [gitlab documentation](https://docs.gitlab.com/ci/testing/code_quality/#merge-request-widget):

![Example gitlab codequality widget](https://docs.gitlab.com/ci/testing/img/code_quality_merge_request_widget_v18_2.png)

# Usage
`$ mypy program.py --output=json | mypy-gitlab-code-quality`

This command send to `STDOUT` generated json that can be used as Code Quality report artifact.

Also, this script supports plain text output parsing for backward compatability but json is recommended.

`$ mypy program.py | mypy-gitlab-code-quality`

## Example .gitlab-ci.yml
```yaml
image: python:alpine
codequality:
  script:
    - pip install mypy mypy-gitlab-code-quality
    - mypy program.py --output=json > mypy-out.json || true  # "|| true" is used for preventing job fail when mypy find errors
    - mypy-gitlab-code-quality < mypy-out.json > codequality.json
  artifacts:
    when: always
    reports:
      codequality: codequality.json
```
Note: if you want to use this example you should replace `program.py` with yours module names.

# Contributing
Please run linters before creating pull request
```shell
pip install requirements/dev.txt
mypy .
ruff check
ruff format
```
Suggestions and pull requests are always welcome :)
