import colorful as cf
import csv
from datetime import datetime, timedelta


# Static methods
cf.update_palette({"blue": "#2e54ff", "green": "#08a91e", "orange": "#ff5733"})


def cal_status_color(status):
    """
    Color response status of calendar attendees.
    :param status: str
    :return: colorful object
    """
    if status == "accepted":
        status = cf.green(status)
    elif status == "needsAction":
        status = cf.orange(status)
    elif status == "declined":
        status = cf.red(status)
    elif status == "tentative":
        status = cf.yellow(status)

    return status


def colorize_table(table):
    """
    Colors nested list green and orange (if ukevakt)
    :param table: nested list
    :return:
    """
    for i in range(len(table)):
        if "X" in table[i]:
            table[i] = map(cf.orange, table[i])
        else:
            table[i] = map(cf.green, table[i])

    return table


def read_roster_csv(filepath):
    title = None
    header = None
    table = list()
    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if header:
                table.append(row)
            if not title and len(row) == 1:
                title = str(row[0])
            if not header and len(row) > 1:
                header = row

    return title, header, table


def week_to_date(year, week):
    """
    converts week number for a given year to date (year-month-day)
    :param year: int
    :param week: int
    :return: first date, last date of week (year-month-day)
    """
    firstdayofweek = datetime.strptime(f'{year}-W{int(week)}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + timedelta(days=6.9)
    return firstdayofweek, lastdayofweek


