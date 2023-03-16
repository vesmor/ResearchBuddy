import requests
from bs4 import BeautifulSoup
from itertools import zip_longest
import time
# from selenium import webdriver

# ACM CHI 
# (This would include CHI conference, CHI Late-breaking work, TOCHI, CHI-Play, etc.)

# Work on getting why some elements arent getting read in properly
# it seems to be because of a <br> or break line

# Make a request to the website
url = 'https://sigchi.org/conferences/upcoming-conferences/'
website = requests.get(url)

time.sleep(1)

# Parse the HTML content using BeautifulSoup
websiteHTML = BeautifulSoup(website.text, 'html.parser')


file = open("fileout.txt", "w", encoding="utf-8")


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
    for a in name.findAll('a', href=True):
        a.extract()

    nameText = name.text
    print(nameText)
    eventNames.append(nameText)


# zip the the list into a tuple together so its the name and date
conferences = zip_longest(eventNames, dates, fillvalue="nothing provided")


offset = 3  #shift by 3 because first two events aren't titled
for index, event in enumerate(conferences): #enumerate so we can use index numbers instead of the stupid pythonic shit
    try:
        # print(event)
        fileLine = str(
                        str(eventNames[index]) + "\n" + 
                        str(dates[index + offset]) + "\n\n"
                    )

        file.write(fileLine) 

    except Exception as err:
        print("not working cuz: {e}".format(e=err))
        pass

file.close()
