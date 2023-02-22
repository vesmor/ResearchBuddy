import subprocess
import discord
from discord import option

import os
from dotenv import load_dotenv
import Calendar.calendar_handler as calendar
import json

from datetime import datetime
from dateutil.parser import parse as dtparse

'''
    If there's a problem logging into the google calendar or you get a "bad auth request" or "invalid_grant" error 
    just delete the token.json file and rerun the program
'''

'''
    custom Exceptions
'''



'''
    TODO:
        Way to delete all events maybe[think about this]
        
'''


class ImpossibleValueError(Exception):
    pass


MAXEVENTS = 8

load_dotenv() #loads all the .env variables
token = os.getenv('TOKEN') #grab token for discord from env file

#TODO: addmore useful error message
if token == None: 
    print("ERROR: No Token found, check you have an .env file in the same directory or token is valid")
    exit(-1)


bot = discord.Bot()

@bot.event
async def on_ready():
    calendar.calendar_setup()
    print("Calendar setup successful")
    print('Logged in as {0.user}'.format(bot))
    
@bot.slash_command(name = "hello", description = "Hello world to ResearchBuddy")
async def helloWorld(message):
    if message.author == bot.user:
        return
    
    await message.respond("Hello everyone! I'm up and alive!")

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
                    start = datetime.strftime(dtparse(start), format=tmfmt) #converts googles API date to a better readable format
                    
                    eventResult = event['summary'] + " will happen on " + start
                    await chat.send_followup(content = eventResult, ephemeral = True)
                except KeyError:
                    await chat.send_response("No events found", ephemeral = True)
            
                
    except ValueError:
        await chat.send_response("numevents must be a number.", ephemeral = True)
    except ImpossibleValueError:
        await chat.send_response("numevents has to be a positive numerical value between 1 and " + str(MAXEVENTS), ephemeral = True)
    

#TODO: create way to add to json file keeping track of dates
@bot.slash_command(name = "addevent", description = "add an event to the calendar")
@option(
    "new_event",
    str,
    description="event description and date and time"
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
@bot.slash_command(name = "deleteevent", description = "add an event to the calendar")
@option(
    "event_name",
    str,
    description="name of event to be deleted"
)
async def delete_event(chat, event_name :str): 
    statusMessage = calendar.delete_event(event_name)
    await chat.respond(statusMessage)
    
    # def check(m): # checking if it's the same user and channel
    #     return m.author == chat.author and m.channel == chat.channel
    
    # try: # waiting for message
    #     response = await bot.wait_for('message', check=check, timeout=10.0) # timeout - how long bot waits for message (in seconds)
    #     if response.content.lower() in ("yes", "y"):
            
    # except TimeoutError: # returning after timeout
    #     return
    

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
    

bot.run(token)