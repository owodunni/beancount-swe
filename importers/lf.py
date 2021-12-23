from decimal import Decimal
from beancount.ingest.importer import ImporterProtocol
from beancount.core.amount import Amount
from beancount.core import data
from typing import Dict
from datetime import datetime, timedelta
import warnings
import csv

def to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def to_decimal(amount_str: str):
    return Decimal(amount_str.replace(' ','').replace(',','.'))

class LfBankImporter(ImporterProtocol):
    def __init__(self, account_info: Dict[str, str], currency="SEK"):
        self.account_info = account_info
        self.currency = currency

        self.date_start = None
        self.date_end = None

        super().__init__()

    def account_name(self, file):
        with open(file.name) as fd:
            line = fd.readline().strip()
            # Second line contains account number
            line = fd.readline().strip()
        if not line:
            return None

        try:
            account_number = line.split(";")[0]
        except ValueError:
            return None
        else:
            account_number = account_number.strip('"')
            if account_number in self.account_info:
                return self.account_info[account_number]

    def identify(self, file):
        return self.account_name(file) is not None

    def extract(self, file):
        account_name = self.account_name(file)
        if account_name is None:
            warnings.warn(f"{file.name} is not compatible with LfBankImporter")
            return []

        with open(file.name) as fd:
            # Skip first 3 lines containing metadata
            fd.readline()
            fd.readline()
            fd.readline()

            reader = csv.DictReader(fd, delimiter=';', quoting=csv.QUOTE_MINIMAL)

            entries = []

            for index, line in enumerate(reader):
                index += 3
                print(line)
                meta = data.new_metadata(file.name, index)
                amount = Amount(to_decimal(line['Belopp']), self.currency)
                date = to_date(line['Transaktionsdatum'])
                description = line['Meddelande']

                postings = [data.Posting(account_name, amount, None, None, None, None)]

                entries.append(
                    data.Transaction(meta, date, self.FLAG, description, description, data.EMPTY_SET, data.EMPTY_SET, postings)
                )
            return entries

    def parse_dates(self, date):
        if self.date_start and self.date_start > date:
            self.date_start = date
        if self.date_end and self.date_end < date:
            self.date_end = date
