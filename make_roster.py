#!venv/bin/python3
"""
Tool to print RT support rost from a staff list (.csv) where individual
staff members settings can be adjusted as needed (frequency, shared shifts, ukevakt).
"""

import random
import datetime
from src.static_methods import week_to_date
from distutils.util import strtobool
from tabulate import tabulate
import colorful as cf
import click
import sys
import re
import os.path
import csv


def read_staff_list(staff):
    """
    :param staff: filepath to list containing staff. Must at minimum contain header #name.
    :return: dictionary with staff members
    """
    if not os.path.isfile(staff):
        print(f"\nCould not find any file {staff} for staff to include in rost.\n"
              f"aborting...")
        sys.exit()

    headers = list()
    staff_members = dict()
    with open(staff, "r") as stafflist:
        for line in stafflist:
            line = re.sub("[\t\n]*", "", line)
            if "#" in line:
                headers += [h.lower().replace("#","").strip() for h in line.split(",")]
                if not "name" in headers:
                    print("could not find #name in staff list.\nAborting...")
                    sys.exit()
            elif len(line.split(",")) == len(headers):
                member = [h.strip() for h in line.split(",")]
                name = member[headers.index("name")]
                staff_members[name] = default_rost_settings()
                for head in headers:
                    if head != "name":
                        staff_members[name][head] = member[headers.index(head)]
            elif len(line.split(",")) == 0:
                print(f"Mismatch between headers and entry in staff list;\n-->{line}")
    return staff_members


def default_rost_settings():
    """
    Default staff roster settings, which can be overwritten by entries in staff.csv
    :return: dict
    """
    return {"email": None, "frequency": 1.0, "ukevakt": True, "shared": False}


def find_next_shift(names_order, rost, staff, ukevakt=False):
    """
    :param names_order: The order of names from random seed
    :param rost: current roster
    :param staff: dict with staff members
    :param ukevakt: bool
    :return:
    """
    who = None
    for name in names_order:
        assign = True
        if ukevakt:
            if not strtobool(staff[name]["ukevakt"]):
                assign = False
        if float(staff[name]["frequency"]) >= current_frequency(name, rost):
            if assign:
                return name
    return who


def current_frequency(who, staff_shifts):
    """

    :param who: Name
    :param staff_shifts: list with shifts, where each shift is a list of names for that shift
    :return: Occurence of who in shifts (fraction of 1)
    """
    if len(staff_shifts) == 0:
        return 0
    shifts = 0

    for shift in staff_shifts:
        shifts += shift.count(who)

    return shifts / len(staff_shifts)


def staff_sharing(who, staff_shifts, staff):
    """
    :param who: name of whom is searching a partner to share shift with
    :param staff: complete staff dict
    :return: list with names that can share shift, if frequency not over the limit
    """
    partners = list()
    for name in staff.keys():
        if name != who:
            if strtobool(staff[name]["shared"]):
                if float(staff[name]["frequency"]) >= current_frequency(name, staff_shifts):
                    partners.append(name)

    if len(partners) == 0:
        return None
    else:
        return partners


def find_share_partner(who, names_order, staff_shifts, staff):
    """
    Look for a partner to share weekly shift with. First look for others that share, than anyone.
    :param who: person searching for a partner to share shift with
    :param names_order: Order of remaining staff members in current round
    :param rost: Current rost list
    :param staff: complete staff dict
    :return: name
    """
    partners = staff_sharing(who, staff_shifts, staff)

    if not partners:
        partners = names_order.copy()

    for name in partners:
        if float(staff[name]["frequency"]) >= current_frequency(name, staff_shifts):
            return name

    return None


def rost_dict_to_staff_list(rost):
    """
    :param rost: rost dict
    :return: list with staff in current rost
    """
    rost_staff = list()
    for week in rost.keys():
        for name in rost[week]["who"]:
            rost_staff.append(name)
    return rost_staff


def print_rost(rost, year, csv=False):
    """
    :param rost: dict
    :param year: int
    :return: headers, table (lists)
    """
    cf.update_palette({"blue": "#2e54ff"})
    cf.update_palette({"green": "#08a91e"})
    cf.update_palette({"orange": "#ff5733"})

    table = list()
    header = ["Week", "From", "To", "Who", "Ukevakt", "email"]
    if csv:
        header_w = header.copy()
        table_w = list()
    header = map(cf.blue, header)

    for w in sorted(rost.keys()):
        d1, d2 = week_to_date(year, w)
        who = '/'.join(rost[w]["who"][:])
        email = '/'.join(rost[w]["email"][:])

        if rost[w]["ukevakt"]:
            table.append(map(cf.orange, [str(w), str(d1), str(d2), who, "X", email]))
            if csv:
                table_w.append([str(w), str(d1), str(d2), who, "X", email])

        else:
            table.append(map(cf.green, [str(w), str(d1), str(d2), who, " ", email]))
            if csv:
                table_w.append([str(w), str(d1), str(d2), who, " ", email])

    title = f"UiT RT SUPPORT weeks {min(rost.keys())} - {max(rost.keys())} {year}"
    print(cf.red(title))
    print(tabulate(table, header, tablefmt="pretty", stralign="left"))

    if csv:
        filename = f"RT_roster_{min(rost.keys())}-{max(rost.keys())}_{year}.csv"
        write_roster_csv(filename, title, header_w, table_w)


def write_roster_csv(filename, title, header, table):
    """
    :param filename: filename/path
    :param title: str
    :param header: list ["title1", "title2",...]
    :param table: nested list [[title 1 stuff], [title 2 stuff],...]
    """

    with open(filename, "w", newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        csvfile.write(f"{title}\n")
        writer.writerow(header)
        writer.writerows(table)


def rost_stats(rost):
    """
    Count shifts and "ukevakt"s in current rost.
    :param rost:
    :return: dict
    """
    shifts = dict()
    for w in rost.keys():
        for who in rost[w]["who"]:
            if who not in shifts.keys():
                shifts[who] = dict()
                shifts[who]["shifts"] = 0
                shifts[who]["shifts total"] = 0
                shifts[who]["ukevakt"] = 0
            shifts[who]["shifts"] += (1. / len(rost[w]["who"]))
            shifts[who]["shifts total"] += 1
            if rost[w]["ukevakt"]:
                shifts[who]["ukevakt"] += 1

    return shifts


def print_stats(rost, shift_rounds):

    shift_stats = rost_stats(rost)
    header = ["Name", "Shifts total", "Ukevakt", "Frequency", "Shifts load", "Load (%)"]
    table = list()

    for name in sorted(shift_stats.keys()):
        shifts = shift_stats[name]["shifts"]
        shifts_total = shift_stats[name]["shifts total"]
        ukevakt = shift_stats[name]["ukevakt"]
        freq = shifts_total / shift_rounds
        load = (shifts / len(rost)) * 100.
        table.append(map(cf.white, map(str, [name, shifts_total, ukevakt, "%.2f" % freq, "%.2f" % shifts, "%.2f" % load])))

    print(tabulate(table, header, floatfmt=".4f", tablefmt="pretty", stralign="left", numalign="right"))


def populate_rost(from_week, to_week, seed, ukevakt, staff):
    """
    :param from_week:
    :param to_week:
    :param year:
    :param ukevakt:
    :param staff:
    :return:
    """
    rost = dict()

    # Randomise order of staff
    # Using seed, so that the same list (order) can be reproduced if necessary
    random.seed(seed)
    names_random = random.sample(list(staff.keys()), len(staff))

    staff_avail = names_random.copy()
    staff_shifts = list()
    shift = list()
    this_weeks_staff = list()

    for week in range(from_week, to_week + 1):
        rost[week] = dict()
        rost[week]["who"] = list()
        rost[week]["email"] = list()
        rost[week]["ukevakt"] = False
        if week in ukevakt:
            rost[week]["ukevakt"] = True

        this_weeks_staff.clear()

        if len(staff_avail) == 0:
            staff_avail = names_random.copy()
            staff_shifts.append(shift.copy())
            shift.clear()

        who = find_next_shift(staff_avail, staff_shifts, staff, rost[week]["ukevakt"])

        if not who:
            staff_avail = names_random.copy()
            staff_shifts.append(shift.copy())
            shift.clear()
            who = find_next_shift(staff_avail, staff_shifts, staff, rost[week]["ukevakt"])

        rost[week]["who"].append(who)
        rost[week]["email"].append(staff[who]["email"])
        shift.append(who)
        staff_avail.remove(who)
        this_weeks_staff.append(who)

        # Check for sharing:
        if strtobool(staff[who]["shared"]):
            partner = find_share_partner(who, staff_avail, staff_shifts, staff)
            if not partner:
                staff_avail = names_random.copy()
                staff_shifts.append(shift.copy())
                shift.clear()
                partner = find_share_partner(who, staff_avail, staff_shifts, staff)
            rost[week]["who"].append(partner)
            rost[week]["email"].append(staff[partner]["email"])
            staff_avail.remove(partner)
            shift.append(partner)

        # Check staff frequency, and add staff to end of staff_avail again if possible
        tmp_shifts = staff_shifts.copy()
        tmp_shifts.append(shift.copy())
        for u in this_weeks_staff:
            if float(staff[u]["frequency"]) > current_frequency(who, tmp_shifts):
                print(f"One more round for {who}")
                staff_avail.append(who)

    staff_shifts.append(shift.copy())

    return rost, len(staff_shifts)


year = datetime.datetime.now().year
from_week = datetime.datetime.now().isocalendar()[1]
to_week = datetime.date(year, 12, 31).isocalendar()[1]
seed = random.randrange(0, 9999)
first_ukevakt = 1
ukevakt_frequency = 4
staff = "staff.csv"
write_file = False

@click.command()
@click.option(
    "-y", "--year", type=int, default=year, help=f"The year to generate roster for (default: {year})."
)
@click.option(
    "-w1", "--from_week", type=int, default=from_week, help=f"First week for roster in {year} (default: {from_week})."
)
@click.option(
    "-w2", "--to_week", type=int, default=to_week, help=f"Final week for roster in {year} (default: {to_week})."
)
@click.option(
    "-u", "--first_ukevakt", type=int, default=first_ukevakt, help=f"First week with ukevakt in {year} "
                                                             f"(default: {first_ukevakt})."
)
@click.option(
    "-f", "--ukevakt_frequency", type=int, default=ukevakt_frequency, help=f"Frequency of ukevakt occurrence "
                                                                   f"(default: {ukevakt_frequency})."
)
@click.option(
    "-s", "--staff", type=str, default=staff, help=f"File with staff for roster (default {staff})."
)
@click.option(
    "-wf", "--write_file", type=bool, default=write_file, help=f"Write roster to csv (default {write_file})."
)
@click.option(
    "--seed", type=int, default=seed, help=f"seed used for random order of staff in rost. Now using {seed}."
)
def main(staff, year, from_week, to_week, seed, first_ukevakt, ukevakt_frequency, write_file):
    """
    CLI for generating a roster over a period of time from a list of staff members (.csv)

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if from_week == datetime.datetime.now().isocalendar()[1] and year != datetime.datetime.now().year:
        from_week = 1

    staff_members = read_staff_list(staff)

    # Weeks with ukevakt (weekly shift):
    ukevakt = [x for x in list(range(first_ukevakt, to_week, ukevakt_frequency)) if x >= from_week]

    print("\n\nGenerating RT support rost with the following settings:")
    print(f"Year: {year}\nFirst week: {from_week}\nFinal week: {to_week}\nFirst ukevakt: {first_ukevakt}\n"
          f"Ukevakt frequency:{ukevakt_frequency}\nUkevakt: {', '.join(map(str, ukevakt))}\n"
          f"Staff: {', '.join(sorted(staff_members.keys()))}\nRandom seed: {seed}\n")

    rost, shifts = populate_rost(from_week, to_week, seed, ukevakt, staff_members)
    print_rost(rost, year, write_file)
    print_stats(rost, shifts)


if __name__ == "__main__":
    main()
