import sys
from src.Gcal_API import GoogleCalendarService
import os

this_file = os.path.abspath(os.path.dirname(__file__))
# scopes may have to be modifed, depending on your permissions for a given calender
# that you have access to.
scopes = ['https://www.googleapis.com/auth/calendar']

# File with keys for Google API
secret_file = f"{this_file}/client_secret.json"

# Tokens file (generated from secret_file). If scopes are changed, this file must be deleted.
if os.path.exists(f"{this_file}/token.json"):
    token = f"{this_file}/token.json"
else:
    token = None

# Default calendars to use (None will automatically guess your personal calendar):
default_cal = None
rt_cal = "1.linje-vaktliste"

# Default attendee for events & updating (email). Leave this as None for automatic setting the parameter
attendee = None

##########################################################################
# If credentials and token are missing - abort!
if not os.path.exists(secret_file) and not os.path.exists(token):
    print(f"Could not find credentials/client_secret.json and token\n{secret_file}\n{token}")
    sys.exit()

# Contact calendar service to get available calenders:
g_cal = GoogleCalendarService(scopes=scopes, credentialsfile=secret_file, token=token)
avail_cal = g_cal.get_calendar_ids
cal_choices = list(avail_cal.keys())


# Remove 'junk' from available calendar choices_
remove = ["Holidays in Norway", "Week Numbers", "Birthdays"]
for junk in remove:
    if junk in cal_choices:
        cal_choices.remove(junk)

# Guess default calendar and attendee if not set by user:
if not default_cal or not attendee:
    for cal in avail_cal.keys():
        if "@" in cal:
            if not default_cal:
                default_cal = avail_cal[cal]
            if not attendee:
                attendee = cal

