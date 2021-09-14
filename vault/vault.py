import sqlite3
import pandas as pd
import ssl
import contextlib
from urllib.request import urlopen
from utils import colored
from lxml import etree

'''
    Get live price for gold
'''
class GoldPrice:
    def __init__(self):
        pass

    def fetch_price(self, currency='USD'):
        url = 'http://www.exchangerates.org.uk/commodities/live-gold-prices/XAU-' + currency + '.html'
        try:
            context = ssl._create_unverified_context()
            with contextlib.closing(urlopen(url, context=context)) as response:

                html = response.read().decode('utf-8')

                dom = etree.HTML(html)
                if currency == 'USD':
                    gold_price = dom.xpath('//*[@id="value_XAUUSD"]/text()')
                else:
                    gold_price = dom.xpath('//*[@id="value_XAUEUR"]/text()')

                return gold_price[0]
        except Exception as e:
            print('Gold error: %s' % str(e))

        return -1

class VaultDatabase:

    def __init__(self):
        self.conn = sqlite3.connect('vault/vault.db')

    def store_price(self, ts, name, amount, price, amount_type='OUNCE'):
        try:
            c = self.conn.cursor()
            #c.execute('''DROP TABLE VAULT''')

            # create table Depot
            c.execute('''CREATE TABLE IF NOT EXISTS VAULT
                         (id integer PRIMARY KEY AUTOINCREMENT, ts timestamp not null, name text not null, amount real, price real, amount_type name, UNIQUE (ts, name))''')

            c.execute('''INSERT INTO VAULT (ts, name, amount, price, amount_type)
                         VALUES(?, ?, ?, ?, ?)''', (ts, name, amount, price, amount_type))

            # commit the changes to db
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(colored(255, 0, 0, 'Data already in the database; ignored'))

    def load_last_data(self):
        df = pd.read_sql_query("SELECT ts, name, amount, price, amount_type FROM VAULT ORDER BY ts", self.conn)
        return df


    def load_last_data_for(self, name):
        df = pd.read_sql_query("SELECT ts, name, amount, price, amount_type FROM VAULT WHERE name=(?) ORDER BY ts DESC", self.conn, params=(name,))
        return df

    def close(self):
        self.conn.close()