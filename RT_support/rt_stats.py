from src.RT_staff import ReadRT
import os
import click
from tabulate import tabulate
import colorful as cf

cf.update_palette({"blue": "#2e54ff", "green": "#08a91e", "orange": "#ff5733"})


def print_days(last_days, top=999):
    headers = ["Owner of tickets ", "Taken", "Solved", "Open", "Activity"]
    table = list()

    total = 0
    solved = 0
    new = 0
    open = 0
    top_ = 0

    sort_ = dict()
    for w in last_days.keys():
        sort_[w] = last_days[w]["new"]

    for w in sorted(sort_, key=sort_.get, reverse=True):
        top_ += 1

        total += last_days[w]['total']
        solved += last_days[w]['solved']
        new += last_days[w]["new"]
        open += last_days[w]["open"]

        if top_ <= top:
            table.append([f"{top_}. {w}", last_days[w]["new"], last_days[w]["solved"], last_days[w]["open"], last_days[w]["total"]])
            if top_ == top:
                table.append([".\n.\n.", ".\n.\n.", ".\n.\n.", ".\n.\n.", ".\n.\n.", ".\n.\n."])

    table.append(map(cf.green, ["TOTAL", new, solved, open, total]))

    print(tabulate(table, map(cf.blue, headers), tablefmt="pretty", stralign="left"))


def print_totals(stats, top=999):
    headers = ["Owner of tickets ",  "Solved", "Open", "Total"]
    table = list()

    total = 0
    solved = 0
    open = 0
    top_= 0

    sort_ = dict()
    for w in stats.keys():
        sort_[w] = stats[w]["total"]

    for w in sorted(sort_, key=sort_.get, reverse=True):
        top_ += 1
        total += stats[w]["total"]
        solved += stats[w]["solved"]
        open += stats[w]["open"]

        if top_ <= top:
            table.append([f"{top_}. {w}", stats[w]["solved"], stats[w]["open"], stats[w]["total"]])
            if top_ == top:
                table.append([".\n.\n.", ".\n.\n.", ".\n.\n.", ".\n.\n."])

    table.append(map(cf.green, ["TOTAL", solved, open, total]))
    print(tabulate(table, map(cf.blue, headers), tablefmt="pretty", stralign="left"))

days = 5
top = 5
print_all = False
file_tsv = "Results.tsv"
@click.command()
@click.option(
    "-f", "--file_tsv", type=str, default=file_tsv, help=f"File (.tsv/.csv) with data (default: {file_tsv})"
)
@click.option(
    "-d", "--days", type=int, default=days, help=f"Print stats from last days (default: {days})"
)
@click.option(
    "-t", "--top", type=int, default=top, help=f"Print top t only (default: {top})"
)
@click.option(
    "-a", "--print_all", type=bool, default=print_all, help=f"Print all stats (default: {print_all})"
)
def main(days, file_tsv, print_all, top):
    """
    Simple CLI to collect stats from rt.uninett.no

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """

    if not os.path.isfile(file_tsv):
        print(f"Could not find {file_tsv}")
        return
    stats = ReadRT(file_tsv)

    last_days = stats.get_last_days(days=days)
    print(f"\n Stats from last {days} days @ rt.uninett.no")
    print_days(last_days, top)

    if print_all:
        print(f"\n Stats for entire period @ rt.uninett.no")
        print_totals(stats.get_staff_totals(), top)


if __name__ == '__main__':
    main()
