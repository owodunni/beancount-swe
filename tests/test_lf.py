from textwrap import dedent

import pytest

from importers.lf import LfBankImporter

account_number = "1234"
account_name = "Assets:Lf:Checking"


@pytest.fixture
def tmp_file(tmp_path):
    return tmp_path / "transactions.csv"


def test_identify_not_correct(tmp_file):
    importer = LfBankImporter({account_number: account_name})

    tmp_file.write_text("Hello World")

    with tmp_file.open() as fd:
        assert not importer.identify(fd)


def test_identify_correct(tmp_file):
    importer = LfBankImporter({account_number: account_name})

    tmp_file.write_text(
        dedent(
            """
            "Kontonummer";"Kontonamn";"";"Saldo";"Tillgängligt belopp"
            "1234";"Buffert";"";"54 000,00";"54 000,00"

            "Bokföringsdatum";"Transaktionsdatum";"Transaktionstyp";"Meddelande";"Belopp"
            "2021-04-27";"2021-04-27";"Betalning";"UNIONENS ARBETSLÖSHETSKASSA";"-170,00"
            """
        ).strip()
    )

    with tmp_file.open() as fd:
        assert importer.identify(fd)
