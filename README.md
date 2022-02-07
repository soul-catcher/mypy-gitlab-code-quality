![Gitlab-CI](https://img.shields.io/badge/GitLab_CI-indigo?logo=gitlab)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-gitlab-code-quality)
[![PyPI](https://img.shields.io/pypi/v/mypy-gitlab-code-quality)](https://pypi.org/project/mypy-gitlab-code-quality/)
![PyPI - License](https://img.shields.io/pypi/l/mypy-gitlab-code-quality)
# mypy-gitlab-code-quality
Simple script to generate [gitlab code quality report](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html)
from output of [mypy](http://www.mypy-lang.org/).

Example gitlab codequality report from [gitlab documentation](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#code-quality-widget):
![Example gitlab codequality report](https://docs.gitlab.com/ee/user/project/merge_requests/img/code_quality_widget_13_11.png)

# Usage
`$ mypy program.py | PYTHONHASHSEED=0 mypy-gitlab-code-quality`

This command send to `STDOUT` generated json that can be used as Code Quality report artifact.

**Note: Set environment variable `PYTHONHASHSEED` to `0` to prevent randomize hashes.**
Constant hashes allow gitlab to determine diff between branches on merge request.

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
    - mypy program.py --no-error-summary > mypy-out.txt
    - PYTHONHASHSEED=0 mypy-gitlab-code-quality < mypy-out.txt > codequality.json
  artifacts:
    when: always
    reports:
      codequality: codequality.json
  allow_failure: true
```
Note: if you want to use this example you should replace `program.py` with yours module names.
