# Contributing to Kalamine

In order to contribute to Kalamine, you need to install the development dependencies. 
After checking out the repository, you can install both the current version of kalamine and those dependencies using `pip install .[dev]`.
Alternatively you can explicitly run `pip install black isort ruff pytest mypy types-PyYAML`.

Then we strongly advise you to setup a git pre-commit hook that check things that will be checked by contnuous integration on GitHub.
You simply need to create inside the project root folder a executable file `.git/hooks/pre-commit` containing:
```bash
#!/bin/sh

echo "Running black" &&
black --check --quiet kalamine &&
echo "Running isort" &&
isort --check --quiet kalamine &&
echo "Running ruff" &&
ruff kalamine &&
echo "Running pytest" &&
pytest --quiet &&
echo "Running mypy" &&
mypy kalamine 
```

This is asking git to run the above commands before any commit is created, and to abort the commit if any of them fail.
You can find more information about those tools on the web sites of 
[black](https://black.readthedocs.io/),
[isort](https://pycqa.github.io/isort/),
[ruff](https://docs.astral.sh/ruff/), 
[mypy](https://mypy.readthedocs.io/), 
[pytest](https://docs.pytest.org/). 
Note that errors flagged by the first three of them can often be automatically fixed, using
`black kalamine`, `isort kalamine` and `ruff --fix kalamine` respectively.


