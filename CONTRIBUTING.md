Contributing to Kalamine
================================================================================


Setup
--------------------------------------------------------------------------------

After checking out the repository, you can install kalamine and its development dependencies like this:

```bash
python3 -m pip install --user .[dev]
```

Which is the equivalent of:

```bash
python3 -m pip install --user -e .
python3 -m pip install --user build black isort ruff pytest mypy types-PyYAML pre-commit
```

There’s also a Makefile recipe for that:

```bash
make dev
```


Code Formating
--------------------------------------------------------------------------------

We rely on [black][1] and [isort][2] for that, with their default configurations:

```bash
black kalamine
isort kalamine
```

Alternative:

```bash
make format
```

[1]: https://black.readthedocs.io
[2]: https://pycqa.github.io/isort/


Code Linting
--------------------------------------------------------------------------------

We rely on [ruff][3] and [mypy][4] for that, with their default configurations:

```bash
black --check --quiet kalamine
isort --check --quiet kalamine
ruff kalamine
mypy kalamine
```

Alternative:

```bash
make lint
```

Many linting errors can be fixed automatically:

```bash
ruff --fix kalamine
```

[3]: https://docs.astral.sh/ruff/
[4]: https://mypy.readthedocs.io


Unit Tests
--------------------------------------------------------------------------------

We rely on [pytest][5] for that, but the sample layouts must be built by
kalamine first:

```bash
python3 -m kalamine.cli make layouts/*.toml
pytest
```

Alternative:

```bash
make test
```

[5]: https://docs.pytest.org


Before Committing
--------------------------------------------------------------------------------

You may ensure manually that your commit will pass the Github CI (continuous integration) with:

```bash
make
```

But setting up a git pre-commit hook is strongly recommended. Just create an executable `.git/hooks/pre-commit` file containing:

```bash
#!/bin/sh
make
```

This is asking git to run the above command before any commit is created, and to abort the commit if it fails.
