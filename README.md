# Setup Dev Environment

First clone this repo then change to the repo directory.

Then run following command:
```sh
pip install poetry
poetry install   # Create virtual environement, install all dependencies for the project
poetry shell     # activate the virtual environment
pre-commit install    # to ensure automatically formatting, linting, type checking and testing before every commit
```

If you want to run unit test manually, just activate virtual environment and run:
```sh
pytest
```