# Contributing to HoneyPy
For those interested in developing for HoneyPy, below I share ways to get started and some of the conventions we use.

## Development
We use poetry for package and dependency management. You can install poetry system-wide with pipx:

```bash
pipx install poetry
```

To lock and install dependencies run

```bash
poetry install
poetry lock
```

To enter the Python virtual environment run

```bash
eval $(poetry env activate)
```

If a suitable Python version cannot be found, it's recommended to use `pyenv` to install it, e.g., `pyenv install 3.13.0`.

Note this doesn't spawn a subshell, so `exit` will close your shell entirely. You could use the poetry shell plugin for more control. Finally, it is important to enter the virtual environment before installing dependencies.

To build the project just run

```bash
poetry build
```

And the source and binary distributions will appear in the `dist/` folder.

## Testing
Run pytest as usual. In the root of the project run
```bash
pytest
```

## Developing plugins and working with HoneyPy source maps
You can develop plugins in a similar way to HoneyPy itself. However, since plugins will depend on HoneyPy, it can be useful to link not to the PyPi-installed version, but to a local copy, for instance for debugging purposes.

Within your environment of your plugin package, use the `--editable` option to install HoneyPy with the source maps

```bash
pip install -e [path]
```

Then your dependency updates with the changes made locally, and even the debugger and IntelliSense will take note of this.

## Testing
Run pytest as usual. In the root of the project run
```bash
pytest
```

And tox tests in python 3.13 can be run with, say
```bash
tox -e py313 -- --randomly-seed=1234
```
The seed is optional, and will shuffle the order of the tests and is good practice.
To run the full suite with linting, formatting and type-checking, you will need to install black, isort, autoflake, flake8 and mypy with pipx, and run `tox`.

## Lint and Typecheck Locally
Install `black`, `isort`, `autoflake`, `flake8`, `mypy`, `pydocstyle` system-wide with `pipx` or in your environment with `pip`. Go to the repository root and run `black .`, `isort .`, `autoflake .`, `flake8 .`, `mypy .` and `pydocstyle` to lint/format/type-check.

It is recommended to run the corresponding tox environments for these commands; for instance, running `mypy .` in the way it is done in CI runs will probably require a few extra dependencies already taken into account by the `tox.ini` file.

## Commits and Semantic Versioning
We bump our releases and update our changelog automatically, but this requires commits to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) scheme. We use a combination of [release-please](https://github.com/googleapis/release-please) and [commitlint](https://commitlint.js.org/).

We recommend using squash-merge for pull requests for many reasons. Rebase-merge works too, but if you're doing something like red/green development and did not validate all your individual commits against the actions, the main branch may not be clean after a rebase-merge (in the sense that every commit be "green").

```note
Note: if squashing or rebasing, the commit message must conform to commitlint's rules, otherwise release-please will not create a PR
```
