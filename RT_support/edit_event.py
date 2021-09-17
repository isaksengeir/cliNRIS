
import rt_settings as rt
import click
from src.Gcal_API import RTCalendar

cal = rt.default_cal
event_id = None
do_what = "add"
do_where = "attendee"
# new_value is new text or attendee email... False is for delete events... not needed for that
new_value = None
replace = None
sentence = None


@click.command()
@click.option(
    "-c", "--cal", type=click.Choice(rt.cal_choices, case_sensitive=True),
    default=cal, help=f"Calendar (default: {cal})"
)
@click.option(
    "-d", "--do_what", type=click.Choice(["add", "replace", "delete"], case_sensitive=True),
    default=do_what, help=f"Edit, add or delete something from existing event (default: {do_what})."
)
@click.option(
    "-w", "--do_where", type=click.Choice(["attendee", "summary"], case_sensitive=True),
    default=do_where, help=f"What section in event to edit (default: {do_where})."
)
@click.option(
    "-n", "--new_value", type=str, default=new_value, help=f"New new_value for attendee/summary (default: {new_value})."
)
@click.option(
    "-r", "--replace", type=str, default=replace, help=f"Attendee email to replace with new new_value (default: {replace})."
)
@click.option(
    "-id", "--event_id", type=str, default=event_id, help="ID of event to edit in calendar."
)
def main(do_what, event_id, do_where, new_value, replace, cal):
    """
    Simple CLI to edit/add/delete something in existing event with event ID.

    Suggestions, corrections and feedbacks are appreciated: geir.isaksen@uit.no
    """
    if sentence:
        # debuggin... trying to make the bash script understand sentences...
        print(sentence)
        return

    if not event_id:
        print("No event ID given. Aborting.")
        return

    rt_cal = RTCalendar(calendar_id=rt.avail_cal[cal], scopes=rt.scopes, credentialsfile=rt.secret_file, token=rt.token)

    if cal != rt.default_cal:
        rt_cal.change_calendar(calendar_name=cal)

    print(f"Will {do_what} {do_where} for event ID {event_id} in {cal}")

    if not event_id:
        print(f"Event id missing. Aborting.")
        return
    if do_what == "add" or do_what == "replace":
        if not new_value:
            print(f"Need a new_value to {do_what}... aborting.")
            return

    if do_where == "attendee":
        if do_what == "add":
            print("adding...")
            rt_cal.add_attendee(event_id=event_id, attendee=new_value)
        elif do_what == "replace":
            if not replace:
                print(f"Attendee to replace missing. Aborting.")
                return
            rt_cal.replace_attendee(event_id=event_id, attendee_old=replace, attendee_new=new_value)
        elif do_what == "delete":
            if not replace:
                print(f"No attendee to delete given. Use -r /--replace someone@email.com")
                return
            rt_cal.remove_attendee(event_id=event_id, attendee=replace)
    elif do_where == "summary":
        if do_what == "add":
            rt_cal.add_to_summary(event_id=event_id, new_text=new_value)
        elif do_what == "replace":
            rt_cal.replace_summary(event_id=event_id, new_text=new_value)
        elif do_what == "delete":
            rt_cal.delete_summary(event_id=event_id)

    else:
        pass


if __name__ == '__main__':
    main()
