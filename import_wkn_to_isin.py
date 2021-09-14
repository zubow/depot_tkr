import csv

from consors.consors import Database

'''
    Import WKN to ISIN mapping which is needed to get live price from tradegate
'''
if __name__ == "__main__":

    db = Database()

    with open('tradegate/wkn_isin.txt', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if len(row) == 2:
                db.store_wkn_to_isin(row[0], row[1])

    df = db.load_wkn_to_isin()
    print('WKN to ISIN mapping stored')
    print(df)