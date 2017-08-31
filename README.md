# erste-bank-client

This is a python client for the Erste Bank (Austrian Bank) that allows you to download account statements (Kontoauszüge) as a csv file. It uses George, therefore, the Verfüger needs to be freigeschaltet for George. This is beased forked from AngelVol
### Simple usage:
```python
from erste import ErsteClient
username = 'XXX' # please fill in your Verfügernummer
password = 'XXX' # please fill in your George password
optional
iban ='XXX' # the iban number of the account you want to use
account_id ='XXX' # the iban number of the account you want to use.  
account_index ='X'  #This an in internal index which allows you to access the accounts in the order they come.  Allows for easy access to credit card and ivnetment account where theyre might not be an ibam


client = ErsteClient(username, password, iban=iban)

begin_date = date.today()-timedelta(days=5)
end_date = date.today()
csv_data = client.get_csv(begin_date, end_date)
```

Performance maintainted with using account_id (a bit messy, would prefere a neater approach)


### Prerequisites
```bash
pip install rsa requests
```

### TODO
* It's not available as a pip package right now
* There is a lot more functionality that the client could offer like sending out wire statements etc. For my personal use case, I only need the Kontoauszüge. If you want to add that functionality, I'm happy to accept patches.
* Only tested in Python 2.7. I have no idea if it works in Python 3.
