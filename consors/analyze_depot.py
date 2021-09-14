import matplotlib

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime

import pandas as pd
#import pandas.plotting._converter as pandacnv
#pandacnv.register()
from consors.consors import Database
from utils import colored


def analyze_all(cs_depots, label=None):
    sns.set_style('darkgrid')
    compare_depots(cs_depots, label=label)

    show_top_flops_all_depots(cs_depots, label=label)
    analyze_type_per_category_all_depots(cs_depots, label=label)
    analyze_relative_performance_all_depots(cs_depots, label=label)
    analyze_total_value(cs_depots, label=label)


def analyze_type_per_category_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        analyze_type_per_category(cs, label=cust_label)


def analyze_relative_performance_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        analyze_relative_performance(cs, label=cust_label)


def group_by_wkn_all_depots(cs_depots, label=None):
    amount_per_wkn = {}
    for cs in cs_depots:
        for so in cs.stocks:
            if so.WKN in amount_per_wkn:
                amount_per_wkn[so.WKN] += so.amount
            else:
                amount_per_wkn[so.WKN] = so.amount

    print('*** shares per WKN ***')
    print(amount_per_wkn)


def analyze_total_value(cs_depots, label=None):
    total_value = 0
    for cs in cs_depots:
        total_value += cs.depot_value

    print('**********************')
    print(colored(0, 255, 0, 'Total value of all depots: %.0f €' % (total_value)))
    print('**********************')


def analyze_type_per_category(cs, label=None):
    # analyze type of positions
    value_per_category = {'Zertifikat': 0, 'ETF': 0, 'Aktie': 0}
    for so in cs.stocks:
        if so.type not in value_per_category:
            value_per_category[so.type] = 0
        value_per_category[so.type] += so.total_val_eur

    print('*** ***')
    print(value_per_category)

    sns.barplot(list(value_per_category.keys()), list(value_per_category.values()))
    plt.ylabel('Total value [EUR]')

    t_str = 'Total value per category'
    if label is not None:
        t_str += ' (' + label + ')'
    plt.title(t_str)
    plt.grid()
    plt.show()


def analyze_relative_performance(cs, label=None):
    # analyze rel perf
    v_rel_perf = []
    for so in cs.stocks:
        v = so.rel_perf
        if v is not None:
            v_rel_perf.append(v)

    y = np.asarray(v_rel_perf)
    sns.distplot(y)
    plt.ylabel('Density')
    plt.xlabel('Relative performance [%]')

    t_str = 'Distribution of relative performance'
    if label is not None:
        t_str += ' (' + label + ')'

    plt.title(t_str)
    plt.show()


def show_top_by_rel_perf(depot, top=True, label=None, M=10):
    # analyze rel perf
    v_WKN = []
    v_name = []
    v_rel_perf = []
    for so in depot.stocks:
        v = so.rel_perf
        if v is not None:
            if so.WKN not in v_WKN:
                # add only once
                v_name.append(so.get_short_name())
                v_WKN.append(so.WKN)
                v_rel_perf.append(v)

    idx = np.argsort(v_rel_perf)
    if top:
        best_indices = idx[::-1][:M]
    else:
        best_indices = idx[0:M]

    x = [v_name[bi] for bi in best_indices]
    y = [v_rel_perf[bi] for bi in best_indices]

    sns.barplot(y, x)
    plt.xlabel('Rel. performance [%s]')

    if top:
        t_str = 'Top ' + str(M) + ' positions'
    else:
        t_str = 'Flop ' + str(M) + ' positions'

    if label is not None:
        t_str += ' (' + label + ')'

    plt.title(t_str)
    plt.tight_layout()
    plt.show()


def compare_depots(cs_depots, label=None):

    # if multiple depots
    if len(cs_depots) > 1:
        depot_labels = []
        depot_values = []
        for cs in cs_depots:
            depot_labels.append(cs.depot_owner)
            depot_values.append(cs.depot_value)

        # print all depot values
        fig1, ax1 = plt.subplots()
        ax1.pie(depot_values, labels=depot_labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        t_str = 'Relative size of each depot'
        if label is not None:
            t_str += ' (' + label + ')'

        ax1.set_title(t_str)
        plt.show()

        sns.barplot(depot_labels, depot_values)
        plt.ylabel('Total value [EUR]')

        t_str = 'Absolute value of each depot'
        if label is not None:
            t_str += ' (' + label + ')'
        plt.title(t_str)
        plt.grid()

        plt.show()
    else:
        print('You need more than one depot; skip')


def show_top_flops_all_depots(cs_depots, label=None):
    for cs in cs_depots:
        cust_label = label + ' / ' + cs.depot_owner
        show_top_by_rel_perf(cs, top=False, label=cust_label)
        show_top_by_rel_perf(cs, top=True, label=cust_label)


def plot_depot_values_over_time():
    sns.set()
    fig, ax = plt.subplots()

    db = Database()
    owners = db.get_all_owners()

    for owner in owners:
        df = db.load_owner_depot_as_pn(owner)
        print(df)
        dates = convert_dfts_to_date(df)
        ax.plot(dates, df['total_value'], '*-', label=owner)

    db.close()

    # Major ticks every 6 months.
    fmt_month = mdates.MonthLocator()
    ax.xaxis.set_major_locator(fmt_month)

    # Minor ticks every month.
    fmt_day = mdates.DayLocator()
    ax.xaxis.set_minor_locator(fmt_day)

    # Text in the x axis will be displayed in 'YYYY-mm' format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Format the coords message box, i.e. the numbers displayed as the cursor moves
    # across the axes within the interactive GUI.
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
    ax.grid(True)

    # Rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them.
    fig.autofmt_xdate()
    ax.legend()
    ax.set_ylabel('Depot value [€]')
    ax.set_title('Depot value')
    plt.show()


def show_last_aggregated_depot():
    db = Database()

    owners = db.get_all_owners()

    dfs = []
    for owner in owners:
        df = db.load_last_joined_data_as_pn(owner)
        print('Last depot of %s at %s with total value of %.2f €' % (owner, df['ts'][0], df['total_val_eur'].sum()))
        print(df[['name', 'WKN', 'amount', 'total_val_eur', 'rel_perf']])
        dfs.append(df)

    # concat
    df = pd.concat(dfs)

    amount_df = df.groupby('WKN')[['amount']].sum()
    print('*** Joined depot ***')
    print(amount_df)

    db.close()
    print('*** ***')


def convert_dfts_to_date(df):
    # convert to timestamp
    s_dates = df['ts'].values.tolist()
    dates = []
    for s_date in s_dates:
        date = datetime.strptime(s_date, '%d.%m.%y %H:%M')
        dates.append(date)
    return dates


# run
if __name__ == "__main__":
    # depot value over time
    plot_depot_values_over_time()

    show_last_aggregated_depot()