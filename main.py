import subprocess
import discord
import os
from dotenv import load_dotenv
import Calendar.calendar_handler as calendar
import json

from datetime import datetime
from dateutil.parser import parse as dtparse



'''
    custom Exceptions
'''

class ImpossibleValueError(Exception):
    pass


MAXEVENTS = 7

load_dotenv() #loads all the .env variables
token = os.getenv('TOKEN') #grab token from env file

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

#list upcoming events   
@bot.slash_command(name = "list_upcoming_events", description = "enter cmd with parameter of how many upcoming events you would like to see, or else shows next 5")
async def list_upcoming_events(chat, numevents = 5 ):
    try: 
        
        num = int(numevents)
        
        if(num < 1 or num >  MAXEVENTS):
            raise ImpossibleValueError
        else:
            events = calendar.show_n_events(num)
            text = "Here are the next " + str(num) + " events:"
            await chat.send_response(text, ephemeral = True)
            for event in events:
                tmfmt = '%B %d at %I:%M %p'
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = datetime.strftime(dtparse(start), format=tmfmt) #converts googles API date to a better readable format
                
                eventResult = event['summary'] + " will happen on " + start
                await chat.send_followup(content = eventResult, ephemeral = True)
    except ValueError:
        await chat.send_response("numevents must be a number.", ephemeral = True)
    except ImpossibleValueError:
        await chat.send_response("numevents has to be a positive numerical value between 1 and " + str(MAXEVENTS), ephemeral = True)
    

@bot.slash_command(name = "addevent", description = "add an event to the calendar")
async def add_event(chat):
    await chat.respond("adding event")
    exitStatus = calendar.add_event()
    await chat.respond(exitStatus)
    #TODO: create way to add to json file keeping track of dates


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