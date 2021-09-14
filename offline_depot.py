import time
import datetime

from consors.consors import Database
from tradegate.tradegate import TGDatabase
from utils import colored, human_format
from vault.vault import VaultDatabase


def get_last_depot_value():
    '''
        Load last known price from internal DB
    '''

    db = Database()
    tg_db = TGDatabase()
    wkn_isin = db.load_wkn_to_isin()
    owners = db.get_all_owners()

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
                df = tg_db.load_data_by_isin(ISIN)
                p = float(df['price'].iloc[0])
                n = float(row['amount'])
                ts = df['ts'].iloc[0]
                v = n * p
                print(colored(155, 155, 155, '... %s x %.2f = %.2f €' % (ISIN, n, v)))
                owner_v += v
            except Exception as er:
                print(colored(255, 0, 0, 'Failed to fetch price for : ' + str(row['name']) + ':' + str(er)))
                list_of_ignored_stocks.append(row['name'])
        print(colored(255, 255, 255, 'Result: %s w/ value of %s €' % (owner, human_format(owner_v))))
        total_value += owner_v

    print('******************************************************************************')
    if len(list_of_ignored_stocks) > 0:
        print(colored(255, 0, 0, 'Stocks for which we cannot find price: ' + str(list_of_ignored_stocks)))
    print(colored(0, 255, 0, 'Total value of all depots: %s € (%s)' % (human_format(total_value), ts)))

    db.close()
    tg_db.close()

    return total_value

def get_last_vault_value():
    vault_db = VaultDatabase()

    df = vault_db.load_last_data_for('GOLD')
    if df.empty:
        print(colored(255, 0, 0, 'Vault is empty; please import'))
        return 0

    amount = float(df['amount'].iloc[0])
    last_gold_price_eur = float(df['price'].iloc[0])
    last_vault_ts = df['ts'].iloc[0]

    print('Last gold price: %2.f € (%s)' % (last_gold_price_eur, last_vault_ts))

    total_gold_val = last_gold_price_eur * amount
    print(colored(0, 255, 0, 'Total vault value: %s € (%s)' % (human_format(total_gold_val), last_vault_ts)))

    return total_gold_val

# run
if __name__ == "__main__":
    tv_depot = get_last_depot_value()
    tv_vault = get_last_vault_value()

    tv = tv_depot + tv_vault
    depot_dominance = (tv_depot / tv) * 100

    print(colored(238, 197, 84, '******************************************************************************'))
    print(colored(238, 197, 84, '\u2211=%s € (%.2f%% stocks)' % (human_format(tv), depot_dominance)))
    print(colored(238, 197, 84, '******************************************************************************'))
