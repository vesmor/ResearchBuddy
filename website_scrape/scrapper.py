import requests
from bs4 import BeautifulSoup
from itertools import zip_longest
import json
import os

# ACM CHI 
# (This would include CHI conference, CHI Late-breaking work, TOCHI, CHI-Play, etc.)

def scrape(): 
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
        eventNames.append(nameText)


    offset = 3  #shift by 3 because first two events aren't titled
    conferences = zip_longest(eventNames, dates[offset:], fillvalue="nothing provided")# zip the the list into a tuple together so its the name and date


    living_dir = os.path.dirname(os.path.realpath(__file__)) #get the directory this script lives in

    path_parent = os.path.dirname(living_dir)

    eventsJSONPath = path_parent + "/Calendar/events.json"

    # dump the conference events into the json file and mark the file as having new unread data
    with open(eventsJSONPath, "w", encoding="utf-8") as json_file:

        conferences = list(conferences)

        eventObjArr = [] # will hold the array of events being written to json later

        for index, event in enumerate(conferences): #enumerate so we can use index numbers instead of the stupid pythonic shit
            try:

                event_name = event[0]
                
                # extract the start and end dates provided
                    # Side note: Because of the HTML utf-8 encoding there are two types of dashes used from the
                    # HTML in the website so we have to make sure to split if not one than the other
                
                if ("–" in event[1]):
                    date_span = event[1].split('–')
                else:
                    date_span = event[1].split('-')
                print(date_span)
                
                start_date = date_span[0]
                if(len(date_span) == 1):
                    end_date = ""
                    unspecificied_end = True
                else:
                    end_date = date_span[1]
                    unspecificied_end = False
                
                print("start: " + start_date + "\nend: " + end_date)
                print()

                eventObj = {
                    "name":     event_name,
                    "start":    start_date,
                    "end":      end_date,  
                    "endTimeUnspecified": unspecificied_end
                }
                
                eventObjArr.append(eventObj)

            except AttributeError as err:
                print("{e}\nMake sure event in this loop has not been combined with its index\n".format(e=err))
                pass
            except Exception as err:
                print("Something went wrong trying to parse the events in the website scrapper\n{e}".format(e=err))

        #make sure we actually had any data parsed before marking it as unread
        if (eventObjArr):
            eventObjArr.insert( 0, {"newData": True} )
        else:
            eventObjArr.insert( 0, {"newData": False} ) 

        json.dump(eventObjArr, json_file, indent = 4, ensure_ascii=False)

if __name__ == "__main__":
    scrape()