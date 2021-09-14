from bs4 import BeautifulSoup as html
import requests
import sqlite3
import pandas as pd

from utils import colored

'''
    Fetch stock price from tradegate
'''
class Stock:

    URL_DATA = "https://www.tradegate.de"
    URL_QUERY = URL_DATA + "/orderbuch.php?isin="

    def __init__(self, id):
        self._id = id
        self._query = Stock.URL_QUERY + id
        self._html = html(requests.get(self._query).content, "html.parser")
        self._data = {}
        self._fetchData()

    def _fetchData(self):
        stock_data = {}
        stock_name = self._html.find("div", {"id": "col1_content"}).find("h2").text
        stock_data.update({"name": stock_name})
        tag_parent = self._html.find_all("td", class_="longprice")
        for item in tag_parent:
            if "id" in item.attrs:
                key = item.attrs.get("id")
                value = item.text.replace(" ", "").replace(",", ".").replace("\xa0", "").replace("TEUR", " TEUR")
                stock_data.update({key: value})
            else:
                tag_child = item.find("strong")
                key = tag_child.attrs.get("id")
                value = item.text.replace(" ", "").replace(",", ".").replace("\xa0", "").replace("TEUR", " TEUR")
                stock_data.update({key: value})
        self._data = stock_data

    def getLastPrice(self):
        return self._data['last']


class TGDatabase:

    def __init__(self):
        self.conn = sqlite3.connect('tradegate/tradegate.db')

    def store_price(self, ts, wkn, isin, price):
        try:
            c = self.conn.cursor()
            #c.execute('''DROP TABLE TRADEGATE_PRICE''')

            # create table Depot
            c.execute('''CREATE TABLE IF NOT EXISTS TRADEGATE_PRICE
                         (id integer PRIMARY KEY AUTOINCREMENT, ts timestamp not null, WKN text not null, ISIN text not null, price real, UNIQUE (ts, ISIN))''')

            #for name, wkn, yticker in zip(stock_names, stock_wkn, stock_yticker):
            c.execute('''INSERT INTO TRADEGATE_PRICE (ts, WKN, ISIN, price)
                         VALUES(?, ?, ?, ?)''', (ts, wkn, isin, price))

            # commit the changes to db
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(colored(255, 0, 0, 'Data already in the database; ignored'))

    def load_all_data(self):
        df = pd.read_sql_query("SELECT ts, WKN, ISIN, price FROM TRADEGATE_PRICE ORDER BY ts DESC", self.conn)
        return df


    def load_data_for(self, WKN):
        df = pd.read_sql_query("SELECT ts, WKN, ISIN, price FROM TRADEGATE_PRICE WHERE WKN=(?) ORDER BY ts DESC", self.conn, params=(WKN,))
        return df

    def load_data_by_isin(self, ISIN):
        df = pd.read_sql_query("SELECT ts, WKN, ISIN, price FROM TRADEGATE_PRICE WHERE ISIN=(?) ORDER BY ts DESC", self.conn, params=(ISIN,))
        return df

    def close(self):
        self.conn.close()