import discord
import os
from dotenv import load_dotenv
import Calendar.calendar_handler as calendar
import json

from datetime import datetime
from dateutil.parser import parse as dtparse

load_dotenv() #loads all the .env variables
token = os.getenv('TOKEN') #grab token from env file

#TODO: addmore useful error message
if token == None: 
    print("ERROR: No Token found")
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
    
@bot.slash_command(name = "list_upcoming_events", description = "enter cmd with parameter of how many upcoming events you would like to see, or else shows next 5")
async def list_upcoming_events(chat, num = 5 ):
    num = int(num)
    events = calendar.show_n_events(num)
    await chat.send_response("Here are the events:", ephemeral = True)
    for event in events:
        tmfmt = '%B %d at %I:%M %p'
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = datetime.strftime(dtparse(start), format=tmfmt) #converts googles API date to a better readable format
        
        eventResult = event['summary'] + " will happen on " + start
        await chat.send_followup(content = eventResult, ephemeral = True)

#TEMPORARY COMMAND
@bot.slash_command(name = "shutdown", description = "shutsdown the bot[TEMPORARY COMMAND]")
async def shutdown_s(chat):
    await chat.respond("NOOO PLEASE DONT SEND ME INTO THE ABYSSS")
    exit(0)

bot.run(token)