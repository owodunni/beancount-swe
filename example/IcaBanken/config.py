from beancount_swe import Ib

# Optionally add a dictionary of known transactions to the importer.
# They will be added to the journal with the account specified.
known_transactions = {
    "TheUnion": "Expenses:Union",
    "Klarna Bank Ab": "Expenses:Shopping",
    "ACME co": "Expenses:Shopping",
    "Convini": "Expenses:Fika",
    "1231232 Pressbyrån": "Expenses:Fika",
    "Trygg-Hansa": "Expenses:Insurance",
    **dict.fromkeys(
        ["Vw-Finans", "Parkster / Billogram", "GAS LTD"],
        "Expenses:Car",
    ),
}

ib_account_info = {
    "9274-261 123 8": "Assets:IcaBanken:DebitCard",
    "9274-123 824 9": "Assets:IcaBanken:OtherAccount",
}

CONFIG = [Ib(ib_account_info, known_transactions)]
