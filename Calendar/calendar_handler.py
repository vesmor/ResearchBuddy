from __future__ import print_function

from pytz import timezone

import datetime
import os.path

from dateutil.parser import parse as dtparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

creds = None
service = None

def calendar_setup():

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    global creds
    global service
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try: 
        service = build('calendar', 'v3', credentials=creds)
    except HttpError as error:
        print('An error occurred: %s' % error)
        
    
def show_n_events(numEvents):
    try:    
        global service
        
        # Call the Calendar API
        tz = timezone("EST")
        now = datetime.datetime.now(tz).isoformat()  # 'Z' indicates UTC time
        # numEvents = input("How many up comings event would you like to see?\n")
        print('Getting the upcoming ' + str(numEvents) + ' events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=numEvents, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return ('No upcoming events found.')
        return events
        # Prints the start and name of the next num events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return ("Sorry an error occurred attempting to reach the Google Calendar")

