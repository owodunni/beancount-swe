## Ica Banken Importer

You must manually add your account number to the first line of the file.
Ica Banken does not include this when you download a CSV export for your account (without clearing number).

Only supports SEK currency.

### Example

**Setup**
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run Beancounter**

bean-identify
```
bean-identify config.py ica_account_export.csv
```

bean-extract
```
bean-extract config.py ica_account_export.csv
```

bean-file
```
mkdir archive
bean-file -o archive config.py ica_account_export.csv
```

