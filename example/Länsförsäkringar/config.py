from beancount_swe import LfBankImporter

lf_account_info = {
    "90257378331": "Assets:Lf:Checking",
    "90257569302": "Assets:Lf:Buffert",
}

CONFIG = [LfBankImporter(lf_account_info)]
