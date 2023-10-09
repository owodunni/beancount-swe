import os
from csv import DictReader
from datetime import date
from typing import Dict

from beancount.core import data, flags
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.ingest.importer import ImporterProtocol

from beancount_swe.ib_loader import IBCSV


class Ib(ImporterProtocol):
    def __init__(
        self,
        account_info: Dict[str, str],
        known_transactions: Dict[str, str] = None,
    ):
        self.account_info = account_info

        if known_transactions:
            self.known_transactions = known_transactions
        else:
            self.known_transactions = {}

        self.active_account: str = ""
        self.stat_date: date = None
        self.end_date: date = None

        super().__init__()

    def load_file(self, file) -> IBCSV:
        with open(file.name, "r", encoding="utf-8-sig") as f:
            lines = [line.strip() for line in f.readlines()]

        account_number = lines.pop(0)
        transactions = list(DictReader(lines, delimiter=";"))
        csv_obj = IBCSV(
            account_number=account_number,
            transactions=transactions,
            file_name=file.name,
        )
        if csv_obj.account_number in self.account_info:
            self.active_account = self.account_info[csv_obj.account_number]

        self.stat_date = csv_obj.transactions[-1].Datum
        self.end_date = csv_obj.transactions[0].Datum

        return csv_obj

    def identify(self, file):
        self.load_file(file)
        # print(self.active_account)
        if self.active_account:
            return True

    def extract(self, file, **kwargs):
        csv_obj = self.load_file(file)

        entries = []

        transactions = list(enumerate(csv_obj.transactions, start=1))
        for index, entry in transactions:
            postings = [
                data.Posting(
                    self.active_account,
                    Amount(D(str(entry.Belopp)), "SEK"),
                    None,
                    None,
                    None,
                    None,
                ),
            ]

            if entry.Text in self.known_transactions:
                postings.append(
                    data.Posting(
                        self.known_transactions[entry.Text],
                        Amount(D(str(entry.Belopp * -1)), "SEK"),
                        None,
                        None,
                        None,
                        None,
                    )
                )

            entries.append(
                data.Transaction(
                    meta=data.new_metadata(csv_obj.account_number, index),
                    date=entry.Datum,
                    flag=flags.FLAG_OKAY,
                    payee=entry.Text,
                    narration=entry.Budgetgrupp,
                    tags=set(),
                    links=set(),
                    postings=postings,
                )
            )

        meta = data.new_metadata(csv_obj.file_name, transactions[-1][0])
        data.Balance(
            meta,
            self.end_date,
            self.active_account,
            transactions[-1][1].Saldo,
            None,
            None,
        )
        return entries

    def file_account(self, file):
        return self.active_account

    def file_date(self, file):
        self.load_file(file)
        return self.end_date

    def file_name(self, file):
        _, extension = os.path.splitext(os.path.basename(file.name))
        return f"IcaBanken{extension}"
