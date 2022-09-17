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


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

        # Call the Calendar API
        tz = timezone("EST")
        now = datetime.datetime.now(tz).isoformat()  # 'Z' indicates UTC time
        numEvents = input("How many up comings event would you like to see?\n")
        print('Getting the upcoming ' + numEvents + ' events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=numEvents, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next num events
        for event in events:
            tmfmt = '%d %B, %H:%M %p'
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.datetime.strftime(dtparse(start), format=tmfmt) #converts googles API date to a better readable format
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)

