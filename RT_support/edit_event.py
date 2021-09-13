
import rt_settings as rt
import click
from src.Gcal_API import RTCalendar

cal = rt.default_cal
event_id = None
task = "add"
what = "attendee"

# add, delete, replace

@click.command()
@click.option(
    "-t" "--task", type=click.Choice(["edit", "add", "delete"], case_sensitive=False),
    default=task, help=f"Edit, add or delete something from existing event (default: {task})."
)
@click.option(
    "-w", "--what", type=click.Choice(["attendee", "summary"], case_sensitive=False),
    default=task, help=f"What section in event to edit (default: {task})."
)
@click.option(
    "-id", "--event_id", type=str, default=event_id, help="ID of event to edit in calendar."
)
def main(task, event_id, what):
    """
    Simple CLI to edit/add/delete something in existing event with event ID.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if not event_id:
        print("No event ID given. Aborting.")
        return

    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)

    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    print(f"Will {task} {what} for event ID {event_id} in {cal}")

    # TODO write some intuetive code to edit existing event. Fex changing attendee, adding one more attendee etc...


if __name__ == '__main__':
    main()