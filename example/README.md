# README

We cook our books with Beancount!

## Getting started

Initialize venv:
```
python -m venv venv
source venv/bin/activate
```

Install deps:
```
pip install -r requirements.txt
```

## Usage

1. Download transactions and place them in a folder like `~/Downloads`
2. Extract transactions into Beancount
    ```
    bean-extract config.py ~/Downloads >> transactions.beancount
    ```
3. Archive transactions
    ```
    bean-file -o documents config.py ~/Downloads
    ```
4. Visualize and balance
    ```
    fava transactions.beancount
    ```

### Link invoice to transaction
Placeing invoices so they match the expense account and transaction date will
link them to transactions:
```
cp /path/to/netflix.pdf documents/Expenses/Online/Netflix/2021-01-01.pdf
```

## Structure

The structure is inspired by [Tracking Personal Finance using Python](https://personalfinancespython.com/) which is available in my google books collection