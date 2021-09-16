#!venv/bin/python3

"""RT_staff.py: Classes to collect RT stats for staff members."""

__author__ = "Geir Villy Isaksen"
__copyright__ = "Copyright 2021, Geir Villy Isaksen, UiT The Arctic University of Norway"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Geir Villy Isaksen"
__email__ = "geir.isaksen@uit.no"
__status__ = "Production"

import csv


class Staff:
    def __init__(self):
        self.name = None
        self.email = None
        self.tickets = list()

    def count_status(self, status="solved"):
        k = 0
        for i in self.tickets:
            if i.status == status:
                k += 1
        return k

    @property
    def tickets_tot(self):
        return len(self.tickets)

    @property
    def tickets_solved(self):
        return self.count_status(status="solved")

    @property
    def tickets_open(self):
        return self.count_status(status="open")

    def tickets_last_days(self, days=5):
        tickets = list()
        tickets_new = list()
        for ticket in self.tickets:
            if "timer" in ticket.last_updated or "minutt" in ticket.last_updated:
                tickets.append(ticket)
                if "timer" in ticket.taken or "minutt" in ticket.taken:
                    tickets_new.append(ticket)
            elif "dager" in ticket.last_updated:
                if int(ticket.last_updated.split()[0]) <= days:
                    tickets.append(ticket)
                if int(ticket.taken.split()[0]) <= days:
                    tickets_new.append(ticket)
        return tickets, tickets_new


class Ticket:
    def __init__(self, tsv_row=None):
        self.translate = {"løst": "solved", "åpen": "open", "avvist": "rejected", "stoppet opp": "stopped", "ny": "new"}
        self.id = None
        self.title = None
        self.status = None
        self.queue = None
        self.owner = None
        self.user = None
        self.created = None
        self.taken = None
        self.last_updated = None

        if tsv_row:
            self.tsv_row = tsv_row
            self.read_row()

    def read_row(self):
        self.id = self.tsv_row[0]
        self.title = self.tsv_row[1]
        self.status = self.translate[self.tsv_row[2]]
        self.queue = self.tsv_row[3]
        self.owner = self.tsv_row[4]
        self.user = self.tsv_row[6]
        self.created = self.tsv_row[7]
        self.taken = self.tsv_row[8]
        self.last_updated = self.tsv_row[9]

        if len(self.taken.split()) < 1:
            self.taken = self.last_updated


class ReadRT:
    def __init__(self, rt_tsv=None):
        self.staff = dict()

        if not rt_tsv:
            pass
        self.rt_tsv = rt_tsv
        self.read_tsv()

    def read_tsv(self):
        with open(self.rt_tsv) as tsv:
            rows = csv.reader(tsv, delimiter="\t", quotechar='"')
            for row in rows:
                if row[0] != 'ID':
                    ticket = Ticket(row)
                    if ticket.owner not in self.staff.keys():
                        self.staff[ticket.owner] = Staff()
                        if "(" in ticket.owner:
                            self.staff[ticket.owner].name = ticket.owner.split("(")[1].split(")")[0]
                            self.staff[ticket.owner].email = ticket.owner.split("(")[0]
                        else:
                            self.staff[ticket.owner].name = ticket.owner
                            self.staff[ticket.owner].email = ticket.owner

                    self.staff[ticket.owner].tickets.append(ticket)

    def get_staff_totals(self):
        stats = dict()
        for who in self.staff.keys():
            staff = self.staff[who]
            stats[staff.name] = dict()
            stats[staff.name]["total"] = staff.tickets_tot
            stats[staff.name]["solved"] = staff.tickets_solved
            stats[staff.name]["open"] = staff.tickets_open
        return stats

    def print_sorted_total(self):
        stats = self.get_staff_totals()
        for w in sorted(stats, key=stats.get, reverse=True):
            print("%s %d" % (w, stats[w]["total"]))

    def count_status(self, tickets, status="solved"):
        k = 0
        for ticket in tickets:
            if ticket.status == status:
                k += 1
        return k

    def get_last_days(self, days=5):
        stats = dict()

        for who in self.staff.keys():
            staff = self.staff[who]
            tickets, tickets_new = staff.tickets_last_days(days=days)
            if len(tickets) > 0:
                stats[staff.name] = dict()
                stats[staff.name]["total"] = len(tickets)
                stats[staff.name]["solved"] = self.count_status(tickets=tickets, status="solved")
                stats[staff.name]["open"] = self.count_status(tickets=tickets, status="open")
                stats[staff.name]["new"] = len(tickets_new)

        return stats

    def print_stats_last_days(self, days=5):
        stats = self.get_last_days(days=days)
        total = 0
        solved = 0
        new = 0

        # Let us sort by new tickets taken
        sort_ = dict()
        for w in stats.keys():
            sort_[w] = stats[w]["new"]

        print("      new solved total")

        for w in sorted(sort_, key=sort_.get, reverse=True):
            total += stats[w]['total']
            solved += stats[w]['solved']
            new += stats[w]["new"]
            print(f"{w} {stats[w]['new']} {stats[w]['solved']} {stats[w]['total']}")
        print("-------------------------------")
        print(f"Total {new} {solved} {total}")








