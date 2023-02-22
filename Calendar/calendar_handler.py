from __future__ import print_function
from venv import create

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
SCOPES = ['https://www.googleapis.com/auth/calendar']

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


        if events == None:
            return ('No upcoming events found.')
        else:
            return events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return ("Sorry an error occurred attempting to reach the Google Calendar")


#adds event from string and "smartly" parses it to find a description and valid date
def add_event(userEvent):
    try:
        
        created_event= service.events().quickAdd(
            calendarId= 'primary',
            text= userEvent
        ).execute()
        
        print (created_event['start'])
        
        #format the event time
        tmfmt = '%B %d at %I:%M %p'
        eventTime = created_event['start'].get('dateTime', created_event['start'].get('date'))
        eventTime = datetime.datetime.strftime(dtparse(eventTime), format=tmfmt)
        
        eventTime = "Added event '" + str(created_event['summary']) + "' on " + str(eventTime) + " to Calendar"

        return eventTime
    
    except HttpError as err:
        print('An error occured creating an event: %s' % err)
        return ("error occured while adding event")
    
    
    

def delete_event(eventName :str):
    
    global service
    
    page_token = None
    
    #go thru calendar page by page
    while True:
        events = service.events().list(calendarId='primary', pageToken=page_token).execute() 
        
        for event in events['items']:
            try:
               
                #delete event
                if ( str(event['summary']).casefold() == eventName.casefold() ):
                    service.events().delete(calendarId='primary', eventId=event['id']).execute()
                    return ("Deleted " + event['summary'])
                
                #keep looking for it
                else:
                    pass
            except KeyError:
                pass
            
        page_token = events.get('nextPageToken')
        
        #until theres no more pages of events to go thru
        if not page_token: 
            return ("No event found by that name")
        
    
def search_for_event(eventName: str):
    global service
    
    page_token = None
    
    #go thru calendar page by page
    while True:
        events = service.events().list(calendarId='primary', pageToken=page_token).execute() 
        
        for event in events['items']:
            try:
               
                #return found event
                if ( str(event['summary']).casefold() == eventName.casefold() ):
                    return event
                
                #keep looking for it
                else:
                    pass
            except KeyError:
                pass
            
        page_token = events.get('nextPageToken')
        
        if not page_token:
            return None