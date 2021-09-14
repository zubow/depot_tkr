import os
import argparse

from consors.analyze_depot import analyze_all
from consors.consors import Depot, Database
from utils import colored

def load_depot_from_file(dir):
    cs_depots = []

    for filename in os.listdir(dir):
        qFileName = os.path.join(dir, filename)
        cs = Depot()
        cs.parse(qFileName)
        cs.print()
        cs_depots.append(cs)

    return cs_depots


'''
    Import data (in CSV format) exported from Consors broker 
'''
if __name__ == "__main__":
    # Usage: python import_from_consors_csv.py --plot True --label "7. Sep. 2021" /tmp/consors_csv/07092021/
    parser = argparse.ArgumentParser(description='Parsing CSV files exported from Consors broker')
    # Required positional argument
    parser.add_argument('dir', type=str,
                        help='The folder with the CSV files')
    parser.add_argument('--label', type=str,
                        help='The label to be used for plots')
    parser.add_argument('--plot', type=bool,
                        help='Plot the import depot')
    args = parser.parse_args()

    # store in internal database
    cs_depots = load_depot_from_file(args.dir)
    print(colored(255, 255, 255, '... CSV files parsed'))

    # store in DB
    db = Database()
    db.store_all_depots(cs_depots)
    db.close()
    print(colored(255, 255, 255, '... data stored in database'))

    if args.plot:
        analyze_all(cs_depots, label=args.label)
