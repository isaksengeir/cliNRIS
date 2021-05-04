#!venv/bin/python3

import rt_settings as rt
import click
from datetime import datetime
from src.Gcal_API import RTCalendar

cal = rt.default_cal
week1 = datetime.now().isocalendar()[1]
week2 = None
year1 = datetime.now().year
year2 = year1
when = "today"

@click.command()
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)
@click.option(
    "-w", "--when", type=click.Choice(["today", "week", "month", "year"], case_sensitive=False),
    default=when, help=f"Period ahead to print events for (default: {when})."
)
@click.option(
    "-w1", "--week1", type=int, default=week1, help=f"Print events from this week (default: {week1})."
)
@click.option(
    "-y1", "--year1", type=int, default=year1, help=f"Year for week1 (default: {year1})."
)
@click.option(
    "-w2", "--week2", type=int, default=week2, help=f"Print events ahead to this week (default: {week2})."
)
@click.option(
    "-y2", "--year2", type=int, default=year2, help=f"Year for week2 (default: {year2})."
)

def main(when, cal, week1, year1, week2, year2):
    """
    CLI to print Google calendar events.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    rt_cal = RTCalendar(calendar_id=rt.avail_cal[rt.default_cal], scopes=rt.scopes, credentialsfile=rt.secret_file,
                        token=rt.token)
    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    if week1 != datetime.now().isocalendar()[1] or week2:
        rt_cal.get_print_weeks(week1=week1, year1=year1, week2=week2, year2=year2)
    else:
        rt_cal.get_print_events(when=when)


if __name__ == '__main__':
    main()
