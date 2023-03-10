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


file = open("output.txt", "w", encoding="utf-8")


datesRaw = websiteHTML.find_all("td", {"data-mtr-content": "Dates"})
eventNamesRaw = websiteHTML.find_all("td", {"data-mtr-content": "Conference Name"})

# for linebreak in websiteHTML.find_all('br'):
#     linebreak.extract()
    
    
# html = open("website.html", "w", encoding="utf-8")
# html.write(websiteHTML.prettify())
# html.close()
# file.write(websiteHTML.prettify())

# tbd = websiteHTML.tbody

# trs = tbd.nextSibling
# # file.write(list(trs).__str__())


# for row in trs:
#     for rowData in row.contents:
#         file.write(rowData.__str__())
#         file.write("\n")



dates = []
for date in datesRaw:
    dates.append(date.string)

eventNames = []
for name in eventNamesRaw:
    eventNames.append(name.string)
    

conferences = zip_longest(eventNames, dates, fillvalue="nothing provided")


for index, event in enumerate(conferences): #enumerate so we can use index numbers instead of the stupid pythonic shit
    try:
        print(event)
        fileLine = str(
                    index.__str__() + ": \t\t" + eventNames[index].__str__()+ 
                    "\n\t\t" + dates[index+3].__str__() + "\n\n"    #shift by 3 because first two events aren't titled
                    )
        
        file.write(fileLine) 

    except Exception as err:
        print("not working cuz: {e}".format(e=err))
        pass

file.close()
