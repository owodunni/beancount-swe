# README

We help Sweden cook their books using Beancount since 2022!

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

