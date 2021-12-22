from beancount.ingest.importer import ImporterProtocol
from beancount.core.amount import Amount
from typing import Dict
from datetime import datetime, timedelta
import warnings


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
            return self.account_info[account_number]

    def identify(self, file):
        return self.account_name(file) is not None

    def extract(self, file):
        account_name = self.account_name(file)
        if account_name is None:
            Warnings.warn(f"{file.name} is not compatible with LfBankImporter")
            return []

        with open(file.name) as fd:
            for line_index, line in enumerate(fd):
                if line_index < 4:
                    continue

                values = line.split(";")
                self.parse_date(values[0])

    def parse_dates(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if self.date_start and self.date_start > date:
            self.date_start = date
        if self.date_end and self.date_end < date:
            self.date_end = date
