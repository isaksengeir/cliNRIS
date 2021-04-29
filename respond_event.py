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
@click.option(
    "-r", "--response", type=click.Choice(["accepted", "declined", "tentative", "needsAction"], case_sensitive=True),
    default=response, help=f"Respond to event and update staus (default: {response}"
)
@click.option(
    "-a", "--attendee", type=str, default=attendee, help=f"Attendee responding (default: {attendee})"
)
def main(event_id, cal, attendee, response):
    """
    Simple CLI to respond to Google calendar events. Get the ID from 'print_events.py'.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if not event_id:
        print("No event ID given. Aborting.")
        return

    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)

    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    rt_cal.respond_event(event_id=event_id, attendee=attendee, response=response)


if __name__ == '__main__':
    main()
