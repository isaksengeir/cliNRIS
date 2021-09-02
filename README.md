# RT_support

<strong>Tools for Metacenter.no RT Support roster and Google calendar management</strong>

Run <code>RT_support/install.sh</code> for setting up python3 virtual environment with dependencies given in <code>RT_support/requirements.txt</code>.

RT_support contains a small collection of simple command line interfaces (CLI's):
<ul>
  <li><code>make_roster</code> for automatic generation of a roster from a list of staff (.csv) over a given period of time. This CLI does not require Google services as do the following.</li>
  <li><code>add_shift</code> to add RT support staff to a given week shift, or several from a pre-created roster file.</li>
  <li><code>swap_shifts</code> to swap RT support staff between two existing shifts/events. </li>
  <li><code>respond_event</code> for responding to an event invitation, or changing the respons status.</li>
  <li><code>event_reminder</code> to send email notification to attendee(s) in an event.</li>  
  <li><code>delete_event</code> to remove/delete an existing event.</li>
  <li><code>print_events</code> to print out calendar events for a given week or time ahead.</li>
  <li><code>rt_stats</code> to print statistics from rt.uninent (.csv)</li> 
</ul>

<strong> Using the calendar CLI's</strong>

In order to use the calendar CLI's, you need to be added to the existing RT roster UiT API workspace by sending a request to geir.isaksen@metacenter.no. Creation of a new Google Cloud Platform (GCP) project and enabling the workspace API is explained in more detail <a href=https://developers.google.com/workspace/guides/create-project> here</a>. Note that the metacenter.no organization only has a limited number of allowed workspaces, so please consult before and if creating a new workspace. 


Once you have access to the RT roster management API workspace, you need to download the OAuth client ID credentials called "rt_uit_rost" (under APIs & Services/Credentials) and save this in your local RT_support directory as client_secret.json.
