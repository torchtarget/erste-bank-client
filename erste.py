# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import re
import rsa
import binascii
from cached_property import cached_property



class ErsteClient(object):
    def __init__(self, username, password, iban=None, account_id=None, account_index=None):
        """Setup the Erste Client Object - setting username and password and setting up the account."""
        self.username = username
        self.password = password
        """Account index needed for credit card accoutns as they ahve no iban"""
        self._account_index = account_index
        self._data = None
        self._iban = self.set_iban(iban) # Not always consist with index be careful when using
        self._account_id = self.set_account_id(account_id) # Not always consist with index be careful when using



    @cached_property
    def access_token(self):
        def RSA(n, e, salt, password):
            """ Translated from site javascript code:

                var rsa = new RSAKey();
                rsa.setPublic(modulus, exponent);
                return rsa.encrypt(salt + "\t" + password);
            """
            n = int(n, base=16)
            e = int(e, base=16)
            message = "%s\t%s" % (salt, password)
            cypherbytes = rsa.encrypt(message.encode('utf-8'), rsa.PublicKey(n, e))
            return binascii.b2a_hex(cypherbytes)

        s = requests.Session()
        url = 'https://login.sparkasse.at/sts/oauth/authorize?response_type=token&client_id=georgeclient'
        r = s.get(url)
        # print r.headers
        r = s.post(url, data={
            'javaScript': 'jsOK',
            'SAMLRequest': 'ignore',
        })
        match = re.search(r'var random = "(.*?)";', r.text)
        salt = match.groups()[0]

        match = re.search('name="modulus" value="(.*)?"', r.text)
        modulus = match.groups()[0]

        match = re.search('name="exponent" value="(.*)?"', r.text)
        exponent = match.groups()[0]

        rsaEncrypted = RSA(modulus, exponent, salt, self.password)

        post_data = {
            'rsaEncrypted': rsaEncrypted,
            'saltCode': salt,
            'j_username': self.username
        }
        # print 'post_data: ', post_data
        url = 'https://login.sparkasse.at/sts/oauth/authorize?client_id=georgeclient&response_type=token'
        r = s.post(url, data=post_data, allow_redirects=False)
        # print 'r.headers: ', r.headers
        match = re.search(r'#access_token=(.*?)&', r.headers['location'])
        if match:
            token = match.groups()[0]
            return token

    # print r.text.encode('utf-8')
    @property
    def account_index(self):
        if not self._account_index:
            self._account_index = 0
            self.set_iban(self._iban)
            self.set_account_id(self._account_id)
            print("We are here")
        return(self._account_index)

    @property
    def account_id(self):
        # If an index exists we should check if that is correct
        if self._account_index:
            self._account_id = self.data['collection'][self.account_index].get('id')
        return(self._account_id)

    @property
    def iban(self):
        # Assume self..accountindex is always correct
        account = self.data['collection'][self.account_index]
        if account.get('accountno'):
            self._iban = account.get('accountno').get('iban')
        else:
            self._iban = None
        return(self._iban)


    @cached_property
    def data(self):
        if not self._data:
            r = requests.get('https://api.sparkasse.at/proxy/g/api/my/accounts', headers={'Authorization': 'bearer %s' % self.access_token})
            self._data = r.json()
        return(self._data)


    def set_account_id(self, account_id):
        """Checks if the account_id exists and sets the account_index for this account. Returns none if no iban found."""
        myid = account_id
        if self._account_index:
            self._account_id = None
            if account_id:
                i = 0
                for account in self.data['collection']:
                    if account.get('id') == account_id:
                        self.account_index = i
                        myid = self.account_id
                    else:
                        myid=None
        self._account_id = myid
        return(self._account_id)



    def set_iban(self, iban):
        """Checks if the Iban exists and sets the account_index for this account. Returns none if no iban found."""
        self._iban = None
        if iban:
            i = 0
            for account in self.data['collection']:
                accountno = account.get('accountno')
                i = i+1
                if accountno and accountno.get('iban') == iban:
                    self.account_index = i
            return(self.iban)
        else:
            return(iban)



    def get_csv(self, start_date, end_date):
        """Get a csv output of the selected account"""
        strf_format = '%Y-%m-%dT%H:%M:%S'
        url = 'https://api.sparkasse.at/proxy/g/api/my/transactions/export.csv?from=%(start_date)s&to=%(end_date)s&lang=de&separator=;&mark=%%22&fields=booking,receiver,amount,currency,reference,referenceNumber,valuation' % {'start_date': start_date.strftime(strf_format), 'end_date': end_date.strftime(strf_format)}
        r = requests.post(url,
            data={
                'access_token': self.access_token,
                'id': self.account_id,
            })
        return r.text[1:]



    def get_Balance(self):
        return(get_Saldo(self.account_index))


    def get_Saldo(self,account_index = None):
        """Get account balance."""
        if not account_index:
            account_index = self.account_index
        account = self.data['collection'][account_index]
        account_balance = float(account.get('balance').get('value'))/(10**float(account.get('balance').get('precision')))
        account_currency=account.get('balance').get('currency')
        saldo_return = {"bank": "George"+str(account_index), "saldo": account_balance, "currency": account_currency}
        return(saldo_return)
