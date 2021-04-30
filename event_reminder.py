#!venv/bin/python3

import rt_settings as rt
import click
from src.Gcal_API import RTCalendar

cal = rt.default_cal
event_id = None
response = "accepted"
attendee = rt.attendee

@click.command()
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)
@click.option(
    "-id", "--event_id", type=str, default=event_id, help="ID of event to remove from calendar."
)


def main(event_id, cal):
    """
    Simple CLI to send email reminder for to Google calendar event. Get the ID from 'print_events.py'.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if not event_id:
        print("No event ID given. Aborting.")
        return

    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)

    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    rt_cal.remind_event(event_id=event_id)


if __name__ == '__main__':
    main()
