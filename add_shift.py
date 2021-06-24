###!venv/bin/python3

import rt_settings as rt
from src.static_methods import read_roster_csv, colorize_table
import click
import colorful as cf
from tabulate import tabulate
from datetime import datetime
from src.Gcal_API import RTCalendar
from make_roster import print_rost

year = datetime.now().year
cal = rt.rt_cal
week = datetime.now().isocalendar()[1]
institution = "UiT"
ukevakt = False
file_roster = None
names = None
emails = None


def add_shifts_from_file(roster, cal, institution, year):
    """
    Reads shifts from roster file and adds them to Google calendar.
    :param roster: str (path) to roster file generated with make_roster.py
    :param cal: obj - google calendar service object (RTCalendar / MyCalendar)
    :param institution: str (UiT, UiO, UiB,...)
    :param year: str
    """
    title, header, table = read_roster_csv(roster)
    if title:
        institution = title.split()[0]
        year = title.split()[-1]

    if verify_calendar_push(title, header.copy(), table.copy(), cal):
        for i in range(len(table)):
            shift = list(table[i])
            week = shift[0]
            names = shift[3].split("/")
            emails = shift[5].split("/")

            cal.add_shift(week=week, names=names, emails=emails, institution=institution, ukevakt=ukevakt, year=year)
    else:
        return


def verify_calendar_push(title, header, table, cal):
    """
    Prints out current roster and forces user to verify before committing to pushing to Google calendar.
    :param title: str
    :param header: list
    :param table: nested list
    :param cal: obj - google calendar service object (RTCalendar / MyCalendar)
    :return: bool
    """
    print("\n\n")
    print(cf.blue(title))
    header = map(cf.blue, header)
    table = colorize_table(table)
    print(tabulate(table, header, tablefmt="pretty", stralign="left"))
    push_events = input(cf.red(f"\n-----> Add entire roster to {cal.current_calendar}? (y/n): "))

    if push_events == "y":
        return True
    else:
        print(cf.red("Cancelled by user"))
        return False


@click.command()
@click.option(
    "-f", "--file_roster", type=str, default=file_roster, help=f"Add RT shifts from roster file (default: {file_roster}"
)
@click.option(
    "-w", "--week", type=int,
    default=week, help=f"Week numeber to add RT shift (default: {week})."
)
@click.option(
    "-i", "--institution", type=str, default=institution,
    help=f"Responsible institution for staff (default: {institution})."
)
@click.option(
    "-n", "--names", type=str, multiple=True, default=names, help=f"List of names for weekly shift."
)
@click.option(
    "-e", "--emails", type=str, multiple=True, default=names, help=f"Emails to attendees in weekly shift."
)
@click.option(
    "-u", "--ukevakt", type=bool, default=ukevakt, help=f"Ukevakt (default: {ukevakt})."
)
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)

@click.option(
    "-y", "--year", type=int, default=year, help=f"Year to add shift in (default: {year})."
)
def main(week, names, file_roster, emails, cal, year, institution, ukevakt):
    """
    CLI to add staff to Metacenter RT roster.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if not names and not file_roster:
        print("Names for shift OR file with roster must be given.")
        return

    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)
    if cal != rt.rt_cal:
        rt_cal.change_calendar(calendar_name=cal)

    if file_roster:
        add_shifts_from_file(file_roster, rt_cal, institution, year)
        return

    add_shift = "y"
    if len(emails) < 1:
        add_shift = input(cf.orange("No emails given (staff will not be notified). Add shift anywas? (y/n): "))
    if add_shift == "n":
        return

    print(cf.blue(f"\n--> Assigning {' and '.join(names)} ({institution}) to {cal} in week {week} ({year})."))

    rt_cal.add_shift(week=week, names=names, emails=emails, institution=institution, ukevakt=ukevakt, year=year)


if __name__ == '__main__':
    main()
