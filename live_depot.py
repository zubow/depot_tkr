import time
import datetime

from consors.consors import Database
from tradegate.tradegate import TGDatabase, Stock
from utils import colored, human_format
from vault.vault import VaultDatabase, GoldPrice


def get_current_depot_value(PAUSE_BETWEEN_REQ=0.5):
    '''
        Show live depot value using data from tradegate
        Sources: https://www.tradegate.de/
    '''

    db = Database()
    tg_db = TGDatabase()
    wkn_isin = db.load_wkn_to_isin()
    owners = db.get_all_owners()

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    print(colored(255, 255, 255, '*** Live depot value ' + timestamp + ' ***'))
    total_value = 0
    list_of_ignored_stocks = []
    for owner in owners:
        owner_v = 0

        df = db.load_last_joined_data_as_pn(owner)
        df_merged = df.merge(wkn_isin, on='WKN', how='left')
        print(colored(255, 255, 255, 'Calculating depot for: %s' % (owner)))

        for index, row in df_merged.iterrows():
            try:
                ISIN = row['ISIN']
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                try:
                    time.sleep(PAUSE_BETWEEN_REQ)
                    s = Stock(ISIN)
                    p = float(s.getLastPrice())
                    tg_db.store_price(timestamp, row['WKN'], ISIN, p)
                except Exception as err:
                    print(colored(255, 0, 0, '⚠️ Failed to fetch price for : ' + str(row['name']) + '; take last known value :' + str(err)))
                    df = tg_db.load_data_by_isin(ISIN)
                    p = float(df['price'].iloc[0])

                n = float(row['amount'])
                v = n * p
                print(colored(155, 155, 155, '... %s x %.2f = %.2f €' % (ISIN, n, v)))
                owner_v += v
            except Exception as er:
                print(colored(255, 0, 0, '⚠️ Failed to fetch price for : ' + str(row['name']) + ':' + str(er)))
                list_of_ignored_stocks.append(row['name'])
        print(colored(255, 255, 255, 'Result: %s w/ value of %s €' % (owner, human_format(owner_v))))
        total_value += owner_v

    print('*** ***')
    if len(list_of_ignored_stocks):
        print(colored(255, 0, 0, 'Stocks for which we cannot find price: ' + str(list_of_ignored_stocks)))
    print(colored(0, 255, 0, 'Total value of all depots: %s €' % (human_format(total_value))))

    db.close()
    tg_db.close()

    return total_value

def get_current_vault_value():
    vault_db = VaultDatabase()

    df = vault_db.load_last_data_for('GOLD')

    if df.empty:
        print(colored(255, 0, 0, 'Vault is empty; please import'))
        return 0

    amount = float(df['amount'].iloc[0])

    gp = GoldPrice()
    last_gold_price_eur = float(gp.fetch_price('EUR'))

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    vault_db.store_price(timestamp, 'GOLD', amount, last_gold_price_eur)

    print('Last gold price: %2.f €' % (last_gold_price_eur))

    total_gold_val = last_gold_price_eur * amount
    print('Total gold value: %s €' % (human_format(total_gold_val)))

    return total_gold_val

# run
if __name__ == "__main__":

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    tv_depot = get_current_depot_value()
    tv_vault = get_current_vault_value()

    tv = tv_depot + tv_vault
    depot_dominance = (tv_depot / tv) * 100

    print('\u2211=%s € (%.2f%% stocks), %s' % (human_format(tv), depot_dominance, timestamp))