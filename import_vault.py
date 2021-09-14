import time
import datetime

from vault.vault import VaultDatabase, GoldPrice

ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

vault_db = VaultDatabase()

gp = GoldPrice()
last_gold_price_eur = float(gp.fetch_price('EUR'))
print('Last gold price: %2.f €' % (last_gold_price_eur))

gold_amount = 1.0 # in ounces
vault_db.store_price(timestamp, 'GOLD', gold_amount, last_gold_price_eur)

total_gold_val = last_gold_price_eur * gold_amount
print('Total gold value: %2.f €' % (total_gold_val))