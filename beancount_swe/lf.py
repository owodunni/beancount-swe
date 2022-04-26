import csv
import os.path
import re
import warnings
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict

from beancount.core import data
from beancount.core.amount import Amount
from beancount.ingest.importer import ImporterProtocol


def to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def to_decimal(amount_str: str):
    return Decimal(amount_str.replace(" ", "").replace(",", "."))


class LfBankImporter(ImporterProtocol):
    def __init__(self, account_info: Dict[str, str], currency="SEK"):
        self.account_info = account_info
        self.currency = currency

        self.date_start = None
        self.date_end = None

        super().__init__()

    def extract_meta_data(self, file):
        try:
            with open(file.name) as fd:
                line = fd.readline().strip()
                # Second line contains account number
                line = fd.readline().strip()
        except Exception:
            return None, None
        if not line:
            return None, None

        try:
            meta_data = line.split(";")
            account_number = meta_data[0].strip('"')
            account_balance = to_decimal(meta_data[3].strip('"'))
        except ValueError:
            return None, None

        return account_number, Amount(account_balance, self.currency)

    def find_account_name(self, account_number):
        if account_number in self.account_info:
            return self.account_info[account_number]

    def identify(self, file):
        account_number, _ = self.extract_meta_data(file)
        return self.find_account_name(account_number) is not None

    def to_known_account(self, payee: str):
        number = payee.replace(".", "")
        if number in self.account_info:
            return self.account_info[number], True
        return payee, False

    def extract_date(self, file_name: str):
        """Returns a tuple containing a is_latest, end_date, start_date"""
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", file_name)
        if not dates:
            return False, None, None
        if "senaste" in file_name:
            return True, to_date(dates[0]), None
        return False, to_date(dates[0]), to_date(dates[1])

    def extract(self, file):
        account_number, account_balance = self.extract_meta_data(file)
        account_name = self.find_account_name(account_number)
        if account_name is None:
            warnings.warn(f"{file.name} is not compatible with LfBankImporter")
            return []

        is_latests, self.date_end, _ = self.extract_date(file.name)

        entries = []
        if is_latests:
            entries.append(
                data.Balance(
                    data.new_metadata(file.name, 1),
                    self.date_end + timedelta(days=1),
                    account_name,
                    account_balance,
                    None,
                    None,
                )
            )

        with open(file.name) as fd:
            # Skip first 3 lines containing metadata
            fd.readline()
            fd.readline()
            fd.readline()

            reader = csv.DictReader(
                fd, delimiter=";", quoting=csv.QUOTE_MINIMAL
            )

            for index, line in enumerate(reader):
                index += 3
                meta = data.new_metadata(file.name, index)
                amount = Amount(to_decimal(line["Belopp"]), self.currency)
                date = to_date(line["Bokföringsdatum"])
                description = line["Transaktionstyp"]
                payee, is_known_account = self.to_known_account(
                    line["Meddelande"]
                )

                postings = [
                    data.Posting(account_name, amount, None, None, None, None)
                ]
                if is_known_account:
                    postings.append(
                        data.Posting(payee, -amount, None, None, None, None)
                    )

                entries.append(
                    data.Transaction(
                        meta,
                        date,
                        self.FLAG,
                        payee,
                        description,
                        data.EMPTY_SET,
                        data.EMPTY_SET,
                        postings,
                    )
                )

            return entries

    def file_account(self, file):
        account_number, _ = self.extract_meta_data(file)
        return self.find_account_name(account_number)

    def file_date(self, file):
        self.extract(file)
        return self.date_end

    def file_name(self, file):
        _, extension = os.path.splitext(os.path.basename(file.name))
        return f"Länsförsäkringar{extension}"
