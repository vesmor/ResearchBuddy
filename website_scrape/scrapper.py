import requests
from bs4 import BeautifulSoup
from itertools import zip_longest
import json
import os
# from selenium import webdriver

# ACM CHI 
# (This would include CHI conference, CHI Late-breaking work, TOCHI, CHI-Play, etc.)


# Make a request to the website
url = 'https://sigchi.org/conferences/upcoming-conferences/'
website = requests.get(url)


# Parse the HTML content using BeautifulSoup
websiteHTML = BeautifulSoup(website.text, 'html.parser')

datesRaw = websiteHTML.find_all("td", {"data-mtr-content": "Dates"})
eventNamesRaw = websiteHTML.find_all("td", {"data-mtr-content": "Conference Name"})


# get the text of the dates and put it in list
dates = []
for date in datesRaw:
    dates.append(date.text)

# get text of each event names in the raw data and put them in a list
eventNames = []
for name in eventNamesRaw:

    #extract any links that might be in the same tag as the conference name
    for a in name.find_all('a', href=True):
        a.extract()

    nameText = name.text
    # print(nameText)
    eventNames.append(nameText)


offset = 3  #shift by 3 because first two events aren't titled
conferences = zip_longest(eventNames, dates[offset:], fillvalue="nothing provided")# zip the the list into a tuple together so its the name and date


living_dir = os.path.dirname(os.path.realpath(__file__)) #get the directory this script lives in

path_parent = os.path.dirname(living_dir)

eventsJSONPath = path_parent + "/Calendar/events_ws.json"

# dump the conference events into the json file

# remember to set the newData to true
with open(eventsJSONPath, "w+") as json_file:

    conferences = list(conferences)

    eventObjArr = []

    # print(conferences[0][0])
    for index, event in enumerate(conferences): #enumerate so we can use index numbers instead of the stupid pythonic shit
        try:


            print(event[0])
            date_span = str(event[1]).split('–')
            # print(date_span)
            # start_date = date_span[0]
            # end_date = date_span[1]
            # print("start: " + start_date + " end: " + end_date)

            eventObj = {

                "hello":"World"
                
            }
            eventObjArr.append(eventObj)

        except Exception as err:
            print("not working cuz: {e}".format(e=err))
            pass

    
    eventObjArr.insert(0, { "len": eventObjArr.__len__()})
    json.dump(eventObjArr, json_file, indent = 4)