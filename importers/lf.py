from beancount.ingest.importer import ImporterProtocol
from typing import Dict


class LfBankImporter(ImporterProtocol):
    def __init__(self, account_info: Dict[str, str], currency="SEK"):
        self.account_info = account_info
        self.currency = currency

        super().__init__()

    def identify(self, file):
        with open(file.name) as fd:
            title_line = fd.readline().strip()
            info_line = fd.readline().strip()
        if not title_line or not info_line:
            return False

        try:
            title = title_line.split(";")[0]
            account_number = info_line.split(";")[0]
        except ValueError:
            return False
        else:
            prefix = title.strip('"')
            account_number = account_number.strip('"')
            return prefix == "Kontonummer" and self.account_info[account_number]

    def extract(self, file):
        return []
