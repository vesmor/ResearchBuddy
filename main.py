import discord
import os
from dotenv import load_dotenv
import json

load_dotenv() #loads all the .env variables
token = os.getenv('TOKEN') #grab token from env file

#TODO: addmore useful error message
if token == None: 
    print("ERROR: No Token found")
    exit(-1)


bot = discord.Bot()

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    
@bot.slash_command(name = "hello", description = "Hello world to ResearchBuddy")
async def helloWorld(message):
    if message.author == bot.user:
        return
    
    await message.respond("Hello everyone! I'm up and alive!")
        
        


bot.run(token)