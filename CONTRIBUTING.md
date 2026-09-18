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
python3 -m pip install --user build ruff pytest mypy types-PyYAML pre-commit
```

There’s also a Makefile recipe for that:

```bash
make dev
```


Code Formating
--------------------------------------------------------------------------------

We rely on [ruff] for that, with the isort rule enabled:

```bash
ruff format kalamine
ruff check --fix kalamine
```

Alternative:

```bash
make format
```


Code Linting
--------------------------------------------------------------------------------

We rely on [ruff] and [mypy] for that, with their default configurations:

```bash
ruff format --check kalamine
ruff check kalamine
mypy kalamine
```

Alternative:

```bash
make lint
```

Many linting errors can be fixed automatically:

```bash
ruff check --fix kalamine
```

[ruff]: https://docs.astral.sh/ruff/
[mypy]: https://mypy.readthedocs.io


Unit Tests
--------------------------------------------------------------------------------

We rely on [pytest] for that, but the sample layouts must be built by
kalamine first:

```bash
python3 -m kalamine.cli make layouts/*.toml
pytest
```

Alternative:

```bash
make test
```

[pytest]: https://docs.pytest.org


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
