![Gitlab-CI](https://img.shields.io/badge/GitLab_CI-indigo?logo=gitlab)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-gitlab-code-quality)
[![PyPI](https://img.shields.io/pypi/v/mypy-gitlab-code-quality)](https://pypi.org/project/mypy-gitlab-code-quality/)
[![Downloads](https://static.pepy.tech/badge/mypy-gitlab-code-quality/month)](https://pepy.tech/project/mypy-gitlab-code-quality)
![PyPI - License](https://img.shields.io/pypi/l/mypy-gitlab-code-quality)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# mypy-gitlab-code-quality
Simple script to generate [gitlab code quality report](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html)
from output of [mypy](http://www.mypy-lang.org/).

Example gitlab codequality report from [gitlab documentation](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#code-quality-widget):
![Example gitlab codequality report](https://docs.gitlab.com/ee/ci/testing/img/code_quality_widget_13_11.png)

# Usage
`$ mypy program.py | mypy-gitlab-code-quality`

This command send to `STDOUT` generated json that can be used as Code Quality report artifact.

## Example .gitlab-ci.yml
```yaml
image: python:alpine
variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/
    - .mypy_cache/

before_script:
  - python --version  # For debugging
  - python -m venv venv
  - . venv/bin/activate

codequality:
  script:
    - pip install mypy mypy-gitlab-code-quality
    - mypy program.py --no-error-summary > mypy-out.txt || true  # "|| true" is used for preventing job fail when mypy find errors
    - mypy-gitlab-code-quality < mypy-out.txt > codequality.json
  artifacts:
    when: always
    reports:
      codequality: codequality.json
```
Note: if you want to use this example you should replace `program.py` with yours module names.

# Contributing
Please run linters before creating merge request
```shell
pip install requirements/dev.txt
black .
mypy .
ruff .
```
Suggestions and merge requests are always welcome :)
