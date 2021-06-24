###!venv/bin/python3

import rt_settings as rt
import click
from src.Gcal_API import RTCalendar

cal = rt.default_cal
event_id1 = None
event_id2 = None

@click.command()
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)
@click.option(
    "-id1", "--event_id1", type=str, default=event_id1, help="ID of first shift with staff to swap with..."
)
@click.option(
    "-id2", "--event_id2", type=str, default=event_id2, help="ID of second shift's staff"
)
def main(cal, event_id1, event_id2):
    """
    Simple CLI to swap staff between two RT support shifts by event IDs (print_events.py).

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if not event_id1 or not event_id2:
        print("Missing event IDs. Aborting.")
        return
    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)

    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)
    rt_cal.swap_shifts(event_id1=event_id1, event_id2=event_id2)


if __name__ == '__main__':
    main()
