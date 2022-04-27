# README
[![PyPI version](https://badge.fury.io/py/beancount-swe.svg)](https://badge.fury.io/py/beancount-swe)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/owodunni/beancount-swe/blob/master/LICENSE)![Package workflow](https://github.com/owodunni/beancount-swe/actions/workflows/python-package.yml/badge.svg)[![CodeFactor](https://www.codefactor.io/repository/github/owodunni/beancount-swe/badge)](https://www.codefactor.io/repository/github/owodunni/beancount-swe)

We help Sweden cook their books using Beancount since 2022!

Supported banks:
* Länsförsäkringar

If you want to add your bank to this lists please drop an issue and include a
.csv with your banks format.

## Gettings stated
In the example folder there is a example beancount project which uses [`beancount-swe`](https://github.com/owodunni/beancount-swe) with [`fava`](https://beancount.github.io/fava/) and [`beancount`](https://beancount.github.io/) to manage personal finance from swedish banks.

```
cp examples ~/my-beancount
```

```
cd ~/my-beancount
```

Open `~/my-beancount/README.md` for further instructions on how to use the example project.

## Development

Install:
```
pip install poetry
```

```
poetry install
```

Build:
```
poetry build
```

Test:
```
poetry run pytest
```

Lint:
```
poetry run flake8
```

Fix:
```
poetry run black . && poetry run isort beancount-swe/ tests/
```
