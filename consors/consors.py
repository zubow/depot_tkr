import csv
import sqlite3
import pandas as pd

from utils import float_de_to_en, colored

'''
    Information on each stock like name, type, amount and performance
'''
class Stock:
    def __init__(self, name, WKN, type, amount, buy_price_pl_tx, currency, total_val_eur, abs_perf, abs_perf_currency, rel_perf):
        self.name = name
        self.WKN = WKN
        self.type = type
        self.amount = amount
        self.buy_price_pl_tx = buy_price_pl_tx
        self.currency = currency
        self.total_val_eur = total_val_eur
        self.abs_perf = abs_perf
        self.abs_perf_currency = abs_perf_currency
        self.rel_perf = rel_perf

    def get_short_name(self, N=8):
        sname = (self.name[:N] + '..') if len(self.name) > N else self.name
        return sname

    def print(self):
        print('\tName: %s, WKN %s, type: %s, amount: %s, BUY: %s %s, total: %s EUR, perf (abs): %s %s, perf (rel): %s%%'
              % (self.name, self.WKN, self.type, self.amount, self.buy_price_pl_tx, self.currency, self.total_val_eur, self.abs_perf, self.abs_perf_currency, self.rel_perf))

'''
    A depot contains a set of stocks
'''
class Depot:

    def __init__(self):
        self.stocks = []

    def print(self):
        print('*** Depot ***')
        print('No.: %s' % self.depot_nr)
        print('Owner: %s' % self.depot_owner)
        print('Update: %s' % self.depot_ts)

        print('Value: %s€' % self.depot_value)
        print('Perf (abs): %s€' % self.depot_abs_perf)
        print('Perf (rel): %s%%' % self.depot_rel_perf)

        print('Positions: ')
        for s in self.stocks:
            s.print()

    def parse(self, qFileName):
        print('parsing ... %s' % qFileName)
        with open(qFileName, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')

            line = 1
            for row in reader:
                if line == 2:
                    self.depot_nr = row[0]
                    self.depot_owner = row[1]
                    self.depot_ts = row[2]

                if line == 5:
                    self.depot_value = float_de_to_en(row[0])
                    self.depot_abs_perf = float_de_to_en(row[1])
                    self.depot_rel_perf = float_de_to_en(row[2])

                if line >= 8:
                    # check end
                    if row[0] == '':
                        break

                    # Name;WKN;Gattung;Stück/Nominal;Einstandskurs inkl. NK;Währung/Prozent;Einstandswert;Währung/Prozent;Veränderung Intraday;Kurs;Währung/Prozent;Datum/Zeit;
                    # Handelsplatz;Gesamtwert EUR;Entwicklung absolut;Währung/Prozent;Entwicklung prozentual
                    s = Stock(row[0], row[1], row[2], float_de_to_en(row[3]), float_de_to_en(row[4]), row[5], float_de_to_en(row[13]), float_de_to_en(row[14]), row[15], float_de_to_en(row[16]))
                    self.stocks.append(s)
                line += 1

'''
    Data imported from CSV files is stored internally inside two database tables
'''
class Database:

    def __init__(self):
        self.conn = sqlite3.connect('consors/consors.db')

    def store_all_depots(self, cs_depots):
        for cs in cs_depots:
            self.store_new_snapshot(cs)
        print(colored(0, 255, 0, 'All new imported data stored in database'))

    def store_new_snapshot(self, depot):

        try:
            c = self.conn.cursor()

            # create table Depot
            c.execute('''CREATE TABLE IF NOT EXISTS Depot
                         (id integer PRIMARY KEY AUTOINCREMENT, nr int, owner text not null, ts timestamp, total_value real, abs_perf real, rel_perf real, UNIQUE (nr, ts))''')

            c.execute('''INSERT INTO Depot (nr, owner, ts, total_value, abs_perf, rel_perf)
                         VALUES(?, ?, ?, ?, ?, ?)''', (depot.depot_nr, depot.depot_owner, depot.depot_ts, depot.depot_value, depot.depot_abs_perf, depot.depot_rel_perf))

            depot_id = c.lastrowid
            print('ID: %d' % depot_id)

            # create table Stocks
            c.execute('''CREATE TABLE IF NOT EXISTS Stocks
                         (id integer PRIMARY KEY AUTOINCREMENT, name text not null, WKN text not null, type text, amount real, buy_price_pl_tx real, currency text, total_val_eur real, abs_perf real, abs_perf_currency real, rel_perf real,                       
                         depot_id integer not null, FOREIGN KEY (depot_id) REFERENCES Depot (id))''')

            for so in depot.stocks:
                c.execute('''INSERT INTO Stocks (name, WKN, type, amount, buy_price_pl_tx, currency, total_val_eur, abs_perf, abs_perf_currency, rel_perf, depot_id)
                             VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                so.name, so.WKN, so.type, so.amount, so.buy_price_pl_tx, so.currency, so.total_val_eur, so.abs_perf, so.abs_perf_currency, so.rel_perf, depot_id))

            # commit the changes to db
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(colored(255, 0, 0, 'Data already in the database; ignored'))
        except sqlite3.Error as err:
            print(colored(255, 0, 0, 'Error while inserting into db: %s' % err))
            raise err

    def get_all_owners(self):
        df = pd.read_sql_query("SELECT distinct(owner) FROM Depot ORDER BY owner ASC", self.conn)
        return df['owner'].values.tolist()


    def load_owner_depot_as_pn(self, owner):
        df = pd.read_sql_query("SELECT ts, owner, total_value FROM Depot WHERE owner=(?) ORDER BY ts ASC", self.conn, params=(owner,))
        return df

    def load_last_joined_data_as_pn(self, owner):
        # get last stored entry
        df = pd.read_sql_query("SELECT max(id) as last_id from Depot WHERE owner=(?)", self.conn, params=(owner, ))
        last_id = int(df['last_id'].values[0])

        df = pd.read_sql_query("SELECT d.ts, s.WKN, s.name, s.amount, s.total_val_eur, s.rel_perf FROM Depot as d, Stocks as s "
                               + "WHERE d.id = s.depot_id and d.id = (?) and owner=(?) ORDER BY s.rel_perf DESC", self.conn, params=(last_id, owner,))
        return df


    def load_all_data_as_pn_sorted_by_stockname(self):
        df = pd.read_sql_query("SELECT name, WKN, sum(amount) totalAmount, sum(total_val_eur) totalValue FROM Stocks GROUP BY WKN ORDER BY name", self.conn)
        print(df)
        return df

    def store_wkn_to_isin(self, wkn, isin):

        try:
            c = self.conn.cursor()
            #c.execute('''DROP TABLE WKNISIN''')

            # create table Depot
            c.execute('''CREATE TABLE IF NOT EXISTS WKNISIN
                         (id integer PRIMARY KEY AUTOINCREMENT, WKN text not null, ISIN text not null, UNIQUE (WKN))''')

            #for name, wkn, yticker in zip(stock_names, stock_wkn, stock_yticker):
            c.execute('''INSERT INTO WKNISIN (WKN, ISIN)
                         VALUES(?, ?)''', (wkn, isin))

            # commit the changes to db
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(colored(255, 0, 0, 'Data already in the database; ignored'))

    def load_wkn_to_isin(self):
        # return ISIN for a given german WKN
        df = pd.read_sql_query("SELECT WKN, ISIN FROM WKNISIN ORDER BY WKN", self.conn)
        return df

    def close(self):
        self.conn.close()