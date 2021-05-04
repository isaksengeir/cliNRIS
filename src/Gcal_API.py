#!venv/bin/python3

"""Gcal_API.py: Classes to communicate with Google calendar services."""

__author__ = "Geir Villy Isaksen"
__copyright__ = "Copyright 2021, Geir Villy Isaksen, UiT The Arctic University of Norway"
__credits__ = []
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Geir Villy Isaksen"
__email__ = "geir.isaksen@uit.no"
__status__ = "Production"

from datetime import datetime, timedelta, date
import os.path
from tabulate import tabulate
import colorful as cf
from src.static_methods import cal_status_color, week_to_date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


cf.update_palette({"blue": "#2e54ff", "green": "#08a91e", "orange": "#ff5733"})


class GoogleCalendarService:
    """
    Creates service to communicate with Google calendar using credentials.
    """
    def __init__(self, scopes=None, credentialsfile='client_secret.json',
                 token=None):
        """
        :param scopes: Permissions (https://developers.google.com/identity/protocols/oauth2/scopes#calendar)
        :param credentials: Keys for accessing google api (client secret file)
        :param token: File that stores user's access and refresh tokens
        """

        self.scopes = scopes
        self.credentialsfile = credentialsfile
        self.token = token
        self.verify_args()

        self.credentials = self.validate_token()
        self.calendar = self.start_calender_service()
        self.calendar_ids = self.get_calendar_ids

    def verify_args(self):
        """
        Control scopes, credentialfile and token.
        """
        if not self.scopes:
            raise SystemExit("ABORTING: Google API scopes not defined.\n"
                             "see https://developers.google.com/identity/protocols/oauth2/scopes#calendar")
        if not self.credentialsfile:
            raise SystemExit("ABORTING: No credential file with secret keys defined.\n"
                             "see https://developers.google.com/identity/protocols/oauth2")
        if not self.token:
            if os.path.isfile("token.json"):
                self.token = "token.json"
                print(f"Found {self.token} (delete if you can't connect.)")
            else:
                print(f"No Token file specified. Creating {self.token} from credentials.")

    def validate_token(self):
        """
        :return: credentials
        """
        credentials = None
        if self.token and os.path.exists(self.token):
            credentials = Credentials.from_authorized_user_file(filename=self.token, scopes=self.scopes)
        else:
            print("No Token file. Generating from secret credential file....")

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentialsfile, self.scopes)
                credentials = flow.run_local_server(port=0)
            with open(self.token, "w") as token:
                token.write(credentials.to_json())

        return credentials

    def start_calender_service(self, api="calendar", version="v3"):
        """
        Starts the google calendar service.
        :return: calendar (service) object
        """
        return build(api, version, credentials=self.credentials)

    def print_avail_calendars(self):
        """
        Prints out calendar summary (title) and the corresponding id
        """
        headers = ["Summary", "Calendar ID"]
        table = list()
        avail_cal = self.get_calendar_ids
        for title in avail_cal.keys():
            table.append([title, avail_cal[title]])

        print(tabulate(table, map(cf.blue, headers), tablefmt="pretty", stralign="left"))

    @property
    def get_all_calendars(self):
        """
        :return: list of calendars that user has access to.
        """
        return self.calendar.calendarList().list().execute().get('items', [])

    @property
    def get_calendar_ids(self):
        """
        :return: dict {summary:id}
        """
        cal_ids = dict()
        for cal in self.get_all_calendars:
            cal_ids[cal["summary"]] = cal["id"]
        return cal_ids


class MyCalendar(GoogleCalendarService):
    """
    Subclass of GoogleCalendarService whith focus on one selected calender from the available ones.
    """
    def __init__(self, calendar_id, scopes, credentialsfile, token="token.json"):
        super(MyCalendar, self).__init__(scopes=scopes, credentialsfile=credentialsfile, token=token)

        self.id = calendar_id
        self.cal_name = self.current_calendar

        # future events in myCalendar to print out:
        self.maxResults = 999

    def change_calendar(self, calendar_name=None, calendar_id=None):
        """
        Change calendar to work with. Requires either calendar_name or ID as arg.
        :param calendar_name: str, name of calendar (summary)
        :param calendar_id: str, id of calendar
        :return:
        """
        if not calendar_id and not calendar_name:
            print("Need calendar name or ID to swap.")
            return

        if calendar_name:
            try:
                self.id = self.calendar_ids[calendar_name]
                self.cal_name = calendar_name
            except KeyError:
                print(f"Found no calendar named {calendar_name}")
                return
        elif calendar_id:
            self.id = calendar_id
            self.cal_name = self.current_calendar

        print(f"Swapped to calender ID {self.id}")

    @property
    def current_calendar(self):
        for name in self.calendar_ids.keys():
            if self.calendar_ids[name] == self.id:
                return name
        return None

    @property
    def get_future_events(self):
        """
        :return:
        """
        _from = datetime.utcnow().isoformat() + 'Z'

        events = self.calendar.events().list(
            calendarId=self.id,
            timeMin=_from,
            maxResults=self.maxResults, singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events.get("items", [])

    def get_events(self, from_date, to_date):
        """
        :param from_date: year-month-day
        :param to_date:  year-mont-day
        :return: events
        """
        events = self.calendar.events().list(
            calendarId=self.id,
            timeMin=f"{from_date}T00:00:00Z",
            timeMax=f"{to_date}T23:59:59Z",
            maxResults=self.maxResults, singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events.get("items", [])

    def get_event(self, event_id):
        """
        Get body of a given event (id)
        :param event_id: id of event
        :return: body
        """
        return self.calendar.events().get(calendarId=self.id, eventId=event_id).execute()

    def events_ahead(self, weeks=None):
        today = datetime.now().date()
        weeks_ahead = {"today": 0, "week": 1, "month": 4, "year": 52}
        return self.get_events(str(today), str(today + timedelta(weeks=weeks_ahead[weeks])))

    def set_maxresults(self, n=100):
        """
        :param n: How many results to return from get_future_events query (default=100)
        :return:
        """
        try:
            self.maxResults = int(n)
        except ValueError:
            print(f"Expected integer in set_maxrestuls. Got {type(n)}.")

    def add_event(self, body):
        return self.calendar.events().insert(calendarId=self.id, body=body, sendNotifications=True,
                                             sendUpdates="all").execute()

    def respond_event(self, event_id, attendee, response):
        event = self.get_event(event_id)
        found_attendee = False
        for i in range(len(event["attendees"])):
            if event["attendees"][i]["email"] == attendee:
                event["attendees"][i]["responseStatus"] = response
                found_attendee = True
        if not found_attendee:
            print(f"Could not find attendee {attendee} in event ID {event_id}")
            return

        event_updated = self.calendar.events().update(calendarId=self.id, eventId=event_id, body=event,
                                                      sendUpdates="all").execute()
        print(f"\nEvent {event_id} updated {event_updated['updated']}")
        print(cf.blue(f"{attendee} status set to: {response}\n"))

    def remind_event(self, event_id):
        """
        Send email notification to attendee(s) in event ID
        :param event_id:
        """
        event = self.get_event(event_id).copy()
        event_starts = datetime.strptime((event["start"]["date"]), '%Y-%m-%d').date()
        today = datetime.today().date()
        print(event_starts)
        print(today)

        days = (event_starts - today).days - 1
        minutes = (days * 24 * 60) + ((23 - datetime.now().hour)*60) + (59 - datetime.now().minute)

        event['reminders'] = {
            'useDefault': False,
             'overrides': [
                {'method': 'email', 'minutes': minutes},
                {'method': 'popup', 'minutes': 10},
             ],
        }
        self.update_event(body=event, event_id=event_id)
        print(f"Email reminder sent to {', '.join(event['attendees']['email'])}.")

    def update_event(self, body, event_id):
        event_updated = self.calendar.events().update(calendarId=self.id, eventId=event_id, body=body,
                                                      sendUpdates="all").execute()
        print(event_updated["updated"])

    def delete_event(self, event_id):
        resp = self.calendar.events().delete(calendarId=self.id, eventId=event_id, sendUpdates="all").execute()
        if len(resp) == 0:
            print(f"Successfully deleted event ID {event_id}")
        else:
            print(resp)


class RTCalendar(MyCalendar):
    """
    Custom calendar class (MyCalendar) for Metacenter RT support events and rosters.
    """
    def __init__(self, calendar_id=None, scopes=None, credentialsfile='client_secret.json', token="token.json"):
        if not scopes:
            scopes = ['https://www.googleapis.com/auth/calendar']
        if not calendar_id:
            calendar_id = "metacenter.no_6e66i3ok59rbrecrg5ck1d5b2o@group.calendar.google.com"

        super(RTCalendar, self).__init__(calendar_id=calendar_id, scopes=scopes, credentialsfile=credentialsfile,
                                         token=token)

    def print_future_events(self, max_results=None):
        if max_results:
            self.maxResults = max_results
        events = self.get_future_events
        self.print_rt_events(events)

    def get_print_events(self, when="today"):
        print(cf.blue(f"* Events {when} in {self.cal_name} *"))
        self.print_rt_events(self.events_ahead(weeks=when))

    def get_print_weeks(self, week1, year1, week2, year2):
        if not week2:
            week2 = week1
        day1 = week_to_date(year=year1, week=week1)[0]
        day2 = week_to_date(year=year2, week=week2)[0]
        print(cf.blue(f"* Events in weeks {week1} ({year1}) - {week2} ({year2}) in {self.cal_name} *"))
        self.print_rt_events(self.get_events(from_date=day1, to_date=day2))

    def print_rt_events(self, events):
        """
        :param max_results:
        :return:
        """
        headers = map(cf.blue, ["Week", "From / To", "Summary", "Attendees", "Status", "Event id"])

        table = list()
        for event in events:
            needs_attention = False
            status = ""
            email = ""
            if "attendees" in event.keys():
                for i in range(len(event["attendees"])):

                    who = event["attendees"][i]
                    nl = ""
                    if i < (len(event["attendees"]) - 1):
                        nl = "\n"

                    try:
                        email += who["email"] + nl
                    except KeyError:
                        email += "no@mail.given" + nl
                        pass
                    try:
                        status += f"{cal_status_color(who['responseStatus'])}{nl}"

                    except KeyError:
                        status += "needsAction" + nl
                        pass
            else:
                status += "Who knows..."
                email += "no@email.given"
                needs_attention = True

            summary = event["summary"]
            id = event["id"]
            starts = event['start'].get('dateTime', event['start'].get('date'))
            ends = event['end'].get('dateTime', event['end'].get('date'))

            w1 = date(*map(int, starts.split("T")[0].split("-")[0:3])).isocalendar()[1]
            w2 = date(*map(int, ends.split("T")[0].split("-")[0:3])).isocalendar()[1]

            table.append([f"{w1}\n{w2}", f"{starts}\n{ends}", summary, email, status, id])
            if needs_attention:
                table[-1][-3:-1] = map(cf.red, table[-1][-3:-1])

        print(tabulate(table, headers, tablefmt="fancy_grid", stralign="left"))

    def add_shift(self, week, names, emails, institution="uiT", ukevakt=False, year=None):
        """
        :param year: int
        :param week: int
        :param institution: str, UiT, NTNU, etc...
        :param names: [name1, name2....]
        :param emails: [mail1, mail2...]
        :return:
        """
        if not week or not names:
            print("Missing arguments. Week (int) and names (list) must be provided")

        if not year:
            year = datetime.now().year

        date_ = datetime.strptime(f'{year}-W{int(week)}-1', "%Y-W%W-%w").date()

        # Add (ukevakt) to summary if ukevakt
        uv = ""
        if ukevakt:
            uv = "(ukevakt)"

        attendees = list()
        for email in emails:
            attendees.append({"email": email})

        # All-day event --> change dateTime with date:

        body = {
            'summary': f'{institution}: {"/".join(names)}{uv}',
            'location': "https://rt.uninett.no & https://slack.com/intl/en-no/",
            'description': 'https://scm.uninett.no/sigma2/interndokumentasjon/-/tree/master/support',
            'start': {
                'date': str(date_),
                'timeZone': 'GMT+02:00',
            },
            'end': {
                'date': str(date_ + timedelta(days=5.9)),
                'timeZone': 'GMT+02:00',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': 'useDefault',
            },
            "colorId": 8,
            "anyoneCanAddSelf": True,
            "sendUpdates": "all",
            "sendNotifications": True,
        }
        event = self.add_event(body)
        print(event)

    def swap_shifts(self, event_id1, event_id2):
        """
        Swaps summary and attendees for events with id1 and id2
        :param event_id1:
        :param event_id2:
        :return:
        """

        # Get the events
        event1 = self.get_event(event_id1)
        event2 = self.get_event(event_id2)

        print(cf.red("\nSwapping staff in shifts:"))
        self.print_rt_events(events=[event1, event2])

        uv = ""
        # Look for (ukevakt) and keep this from swapping!
        # 1 --> 2
        if "(ukevakt)" in event2["summary"]:
            uv = " (ukevakt)"
        summary2 = f"{event1['summary'].replace('(ukevakt)','')}{uv}"
        attendees2 = event1["attendees"]

        # 2 --> 1
        uv = ""
        if "(ukevakt)" in event1["summary"]:
            uv = " (ukevakt)"
        summary1 = f"{event2['summary'].replace('(ukevakt)','')}{uv}"
        attendees1 = event2["attendees"]

        event1["summary"] = summary1
        event1["attendees"] = attendees1
        self.update_event(body=event1, event_id=event_id1)

        event2["summary"] = summary2
        event2["attendees"] = attendees2
        self.update_event(body=event2, event_id=event_id2)

        print(cf.red("\nSwap completed:"))
        self.print_rt_events(events=[event1, event2])

