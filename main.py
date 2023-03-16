
'''
    TODO:
        
        -Way to delete ALL events maybe[think about this]]
        
        - Way to delete all events on a certain date (WITH CONFIRMATION)
        
        -Log all applicable events to console and possible an error output folder
        
        -Way to modify the event

        -Scrape website for event dates       
        
        -End program if token is invalid and a new one needs to be granted and print that problem and how to resolve it to
            a file or console
        
        -Find a way to renew token to google calendar automatically
        
        - Work on a notification system for when an event is upcoming probably by checking each day if theres an event coming soon
        and if its close to the date just add it back
'''


'''README:
    If there's a problem logging into the google calendar or you get a "bad auth request" or "invalid_grant" error 
    just delete the token.json file and rerun the program
'''


import subprocess
import discord
from discord import option
from discord.ext import commands, tasks

import os
from dotenv import load_dotenv
import Calendar.calendar_handler as calendar
import json

import datetime
from dateutil.parser import parse as dtparse


'''
    custom Exceptions
'''
class ImpossibleValueError(Exception):
    pass


#-----------------------CONSTANTS---------------------------------#
MAXEVENTS = 8

load_dotenv() #loads all the .env variables
TOKEN = os.getenv('TOKEN') #grab token for discord from env file

#TODO: addmore useful error message
if TOKEN == None: 
    print("ERROR: No Token for discord found, check you have an .env file in the same directory or token is valid")
    exit(-1)

bot = discord.Bot()

EVENTSJSON = "Calendar/events.json"

#---------------------------------------------------------------------------------------------------------------#



#TODO: place calendar successful message in a place that actually checks if it was successful
@bot.event
async def on_ready():
    calendar.calendar_setup()
    print("Calendar setup successful")
    print('Logged in as {0.user}'.format(bot))
    check_json_for_events.start()
    
   
@bot.slash_command(name = "hello", description = "say Hello to ResearchBuddy")
async def helloWorld(message):
    if message.author == bot.user:
        return
    
    await message.respond("Hello everyone! I'm up and alive!")



#TODO: events in json file need to be deleted once they've passed
#TODO: place event strings into parser and change the newData value to false
@tasks.loop(seconds = 10)
async def check_json_for_events():

    #pass it into the calendar.add_event()
    
    print("\nRunning json parsing job:\n")
    
    #check file exists first
    fileExists = os.path.isfile(EVENTSJSON)
    if (fileExists == False):
        print("{filename} does not exist or is named incorrectly".format(filename = EVENTSJSON))
        print("Stopping the check_json_for_events task. Try renaming or adding an events.json file and restarting bot.")
        check_json_for_events.cancel()
        return
    
    events_file = open(EVENTSJSON, "r+") #read and write access
    
    events = json.load(events_file)
    newData = events[0]["newData"]
    if (not newData):
        events_file.close()
        print("\tNo new data to add")
        return
    
    failedStr = "error occured while adding event"
    for event in events[1:]:    #ignore the first element in events because it holds newData value
        try:
            
            eventString = ""
        
            if(event["endTimeUnspecified"]):
                eventString = str(event["name"]) + " on " + str(event["start"])
            else:    
                eventString = str(event["name"]) + " from " + str(event["start"]) + " to " + str(event["end"])
            
            print("\t{str}".format(str=eventString))
            returnState = calendar.add_event(eventString)
            returnState = str(returnState)

            if (returnState == failedStr):
                print("There was a problem adding {eventName} to the Calendar from events.json".format(eventName = event["name"]))
                pass
            else:
                events.remove(event) #remove event from file since we're adding it to calendar
            
            
        except KeyError as ke:
            print("\nERROR:\n\t{err}: key is trying to be accessed. It might not exist in the events.json file\n".format(err = ke))
            events_file.close()
            return
        except Exception as err:
            print("Something in general went wrong while trying to run json checking task or do something within that task")
            print("Here is the error message {errm}".format(errm=err))
            events_file.close()
            return
            
    #file has been read and has nothing new to add
    events[0]["newData"] = False
    events_file.seek(0) #set pointer back to beginning to write
    json.dump(events, events_file, indent = 4)
    events_file.truncate() #remove remaining parts
    
    print("\n")   
    events_file.close()
    


#--------------calendar commands ----------------------#


@bot.slash_command(name = "upcoming_events", description = "list the next few upcoming events")
@option(
    "numevents",
    int,
    description= ("number of events in the future you'd like to see up to " + str(MAXEVENTS))
)
async def list_upcoming_events(chat, numevents = 5 ):
    try: 
        
        num = int(numevents)
        
        if(num < 1 or num >  MAXEVENTS):
            raise ImpossibleValueError
        else:
            events = calendar.show_n_events(num)
            text = "Here are the next " + str(num) + " events:"
            await chat.send_response(text, ephemeral = True)
            
            # Prints the start and name of the next num events
            for event in events:
                try:
                    tmfmt = '%B %d at %I:%M %p'
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    start = datetime.datetime.strftime(dtparse(start), format=tmfmt) #converts googles API date to a better readable format
                    
                    eventResult = event['summary'] + " will happen on " + start
                    await chat.send_followup(content = eventResult, ephemeral = True)
                except KeyError:
                    await chat.send_response("No events found", ephemeral = True)
            
                
    except ValueError:
        await chat.send_response("numevents must be a number.", ephemeral = True)
    except ImpossibleValueError:
        await chat.send_response("numevents has to be a positive numerical value between 1 and " + str(MAXEVENTS), ephemeral = True)
    

#TODO: create way to add to json file keeping track of dates
@bot.slash_command(name = "add_event", description = "add an event to the calendar")
@option(
    "new_event",
    str,
    description = "Enter an event description followed by date and time"
)
async def add_event(chat, new_event: str):
    try:
        await chat.respond("adding event")
        exitMessage = calendar.add_event(new_event)
        await chat.respond(exitMessage)
    
    except ValueError:
        await chat.respond("Input wasn't valid")
    except KeyError:
        await chat.respond("Title of event was empty")
    

#deletes an event
#TODO: add confirmation message
@bot.slash_command(name = "delete_event", description = "delete an event from the calendar using name")
@option(
    "event_name",
    str,
    description="name of event to be deleted"
)
async def delete_event(chat, event_name :str): 
    statusMessage = calendar.delete_event(event_name)
    await chat.respond(statusMessage)
    
    

@bot.slash_command(name = "search_event", description = "get the date and info for a calendar event")
@option(
    "event_name",
    str,
    description="name of event to look for"
)
async def search_event(chat, event_name :str):
    
    event = calendar.search_for_event(event_name)
    
    if (event == None):
        await chat.respond("No event of that name found.")
        return
    
    #format event time
    tmfmt = '%B %d at %I:%M %p'
    eventDateTime = event['start'].get('dateTime', event['start'].get('date'))
    eventDateTime = datetime.datetime.strftime(dtparse(eventDateTime), format=tmfmt)
    
    event_desc = str(event['summary']) + " is happening on " + str(eventDateTime)
    await chat.respond(event_desc)
    

#------TEMPORARY COMMANDS---------
@bot.slash_command(name = "shutdown", description = "shutsdown the bot[TEMPORARY COMMAND]")
async def shutdown_s(chat):
    await chat.respond("NOOO PLEASE DONT SEND ME INTO THE ABYSSS")
    
    bot.close()
    exit(0)
    
@bot.slash_command(name = "restart", description = "restarts the bot[TEMPORARY COMMAND]")
async def restart(chat):
    await chat.respond("I'll be back")
    path = os.getcwd() + "/run.bat"
    subprocess.call([path])
    exit(1)
    

bot.run(TOKEN)