from decimal import Decimal
import pytest

from importers.lf import LfBankImporter
from beancount.core.data import Transaction
from textwrap import dedent
from datetime import date

account_number = "1234"
account_name = "Assets:Lf:Checking"

account_number2 = "12345678913"
account_name2 = "Assets:Lf:Savings"

tx_header = dedent(
    """
    "Kontonummer";"Kontonamn";"";"Saldo";"Tillgängligt belopp"
    "1234";"Buffert";"";"54 000,00";"54 000,00"
    """
).strip()

tx_columns = dedent(
    """
    "Bokföringsdatum";"Transaktionsdatum";"Transaktionstyp";"Meddelande";"Belopp"
    """
).strip()

tx_single = dedent(
    """
    "2021-04-27";"2021-04-27";"Betalning";"Netflix";"-99,00"
    """
).strip()

tx_single_known = dedent(
    """
    "2021-04-27";"2021-04-27";"Överföring";"1234.56.789.13";"-99,55"
    """
).strip()

tx_multi = dedent(
    """
    "2021-04-25";"2021-04-25";"Överföring";"1234.56.789.12";"-10 000,00"
    "2021-04-23";"2021-04-23";"Överföring";"VOLVO AB";"3000,00"
    """
)


def create_tx(transactions, header=tx_header, columns=tx_columns):
    return f"{header}\n\n{columns}\n{transactions}"


@pytest.fixture
def tmp_file(tmp_path):
    return tmp_path / "transactions.csv"


@pytest.fixture
def importer():
    return LfBankImporter(
        {account_number: account_name, account_number2: account_name2}
    )


def test_identify_not_correct(tmp_file, importer):
    tmp_file.write_text("Hello World")

    with tmp_file.open() as fd:
        assert not importer.identify(fd)


def test_identify_correct(tmp_file, importer):
    tmp_file.write_text(create_tx(tx_single))

    with tmp_file.open() as fd:
        assert importer.identify(fd)


def test_extract_empty_file(tmp_file, importer):
    tmp_file.write_text(create_tx(""))

    with tmp_file.open() as fd:
        directives = importer.extract(fd)

    assert len(directives) == 0


def assert_tx(transaction, payee, description, date):
    assert isinstance(transaction, Transaction)
    assert transaction.payee == payee
    assert transaction.narration == description
    assert transaction.date == date


def assert_posting(posting, amount, currency="SEK"):
    assert posting.units.number == amount
    assert posting.units.currency == currency


def test_extract_single_tx(tmp_file, importer):
    tmp_file.write_text(create_tx(tx_single))

    with tmp_file.open() as fd:
        directives = importer.extract(fd)

    assert len(directives) == 1
    transaction = directives[0]
    assert_tx(transaction, "Netflix", "Betalning", date(2021, 4, 27))

    assert len(transaction.postings) == 1
    assert_posting(transaction.postings[0], Decimal("-99"))


def test_extract_single_tx_other_account(tmp_file, importer):
    tmp_file.write_text(create_tx(tx_single_known))

    with tmp_file.open() as fd:
        directives = importer.extract(fd)

    assert len(directives) == 1
    transaction = directives[0]
    assert_tx(transaction, account_name2, "Överföring", date(2021, 4, 27))

    assert len(transaction.postings) == 2
    assert_posting(transaction.postings[0], Decimal("-99.55"))
    assert_posting(transaction.postings[1], Decimal("99.55"))


def test_extract_multiple_tx(tmp_file, importer):
    tmp_file.write_text(create_tx(tx_multi))

    with tmp_file.open() as fd:
        directives = importer.extract(fd)

    assert len(directives) == 2
    assert_tx(directives[0], "1234.56.789.12", "Överföring", date(2021, 4, 25))
    assert_posting(directives[0].postings[0], Decimal("-10000"))

    assert_tx(directives[1], "VOLVO AB", "Överföring", date(2021, 4, 23))
    assert_posting(directives[1].postings[0], Decimal("3000"))
