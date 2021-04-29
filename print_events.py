#!venv/bin/python3

import rt_settings as rt
import click
from datetime import datetime
from src.Gcal_API import RTCalendar

year = datetime.now().year
cal = rt.default_cal
when = "today"

@click.command()
@click.option(
    "-w", "--when", type=click.Choice(["today","week", "month", "year"], case_sensitive=False),
    default=when, help=f"Period to print events for  (default: {when})."
)
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)
def main(when, cal):
    """
    CLI to print Google calendar events.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    rt_cal = RTCalendar(calendar_id=rt.avail_cal[rt.default_cal], scopes=rt.scopes, credentialsfile=rt.secret_file,
                        token=rt.token)
    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    rt_cal.get_print_events(when=when)


if __name__ == '__main__':
    main()
