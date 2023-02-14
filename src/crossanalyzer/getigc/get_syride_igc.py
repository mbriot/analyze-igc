import logging
import os
from tracemalloc import start
import requests
import shutil
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

ID_PAYS=66

class Syride :

    def __init__(self, minDistance, maxDistance, minPlafond, spotId, maxTraceToGet, startAtPage, outputDir):
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.minPlafond = minPlafond
        self.spotId = spotId
        self.maxTraceToGet = maxTraceToGet
        self.startAtPage = startAtPage
        self.outputDir = outputDir

    def getFlights(self):
        logger.debug(f"start getting flights for spot ID {self.spotId}")
        flights = getFlightsList(self.spotId, self.minPlafond, self.minDistance, self.maxDistance, self.maxTraceToGet, self.startAtPage)
        logger.debug(f"nbre de vols trouvés : {len(flights)}")

        if os.path.exists(self.outputDir):
            shutil.rmtree(self.outputDir, ignore_errors=True)
        os.mkdir(self.outputDir)

        for flight in flights:
            logger.debug(f"get key for {flight['piloteName']}, number {flight['flightNumber']}")
            key = getFlightKey(flight['flightNumber'])
            flight['key'] = key
            flight['flightIgcUrl'] = f"https://www.syride.com/scripts/downloadIGC.php?idSession={flight['flightNumber']}&key={flight['key']}"
            saveFlight(flight, self.outputDir)

def getFlightsList(spotId, minPlafond, minDistance, maxDistance, maxTraceToGet, startAtPage):
    flights = []
    page_number = startAtPage
    need_exit = False
    while True :
        flightsListUrl = getFlightsListUrl(spotId, page_number)

        page = requests.get(flightsListUrl)
        logger.debug(f"request for page {page_number} : {page.status_code}")
        soup = BeautifulSoup(page.content, "html.parser")
        table = soup.find("table")

        for row in table.find_all("tr", class_="lineDiv"):
            cols = row.find_all("td")
            piloteName = cols[0].find("a", href=True)['href'].replace("/fr/pilotes/","")
            distance = cols[2].text.replace("Kilomètres","")
            plafond = cols[3].text.replace("mètres","")
            date = cols[5].text.replace("\t","").replace("\n"," ").strip()
            flightNumber = re.search(r'showFlight\(\'[^\']+\',(\d+),\);', cols[6].get('onclick')).group(1)
            if int(distance) >= minDistance and int(distance) <= maxDistance and int(plafond) >= minPlafond:
                logger.debug(f"{piloteName}, {date}, plaf : {plafond}, distance : {distance}")
                flights.append({"flightNumber" : flightNumber, "piloteName": piloteName, "distance": distance, "date": date})
                if len(flights) == maxTraceToGet :
                    need_exit = True
                    break
            else :
                if int(distance) < minDistance :
                    logger.debug("Out of criteria, exit loop before next page")
                    need_exit = True
        if need_exit :
            break
        else:
            page_number = page_number + 1
    return flights
            
def saveFlight(flight, path):
    fileName = f"{flight['piloteName'].lower()}-{flight['date']}.igc".replace(" ","-").replace("/","-")
    with open(f"{path}/{fileName}", "w") as file:
        igc = requests.get(f"https://www.syride.com/scripts/downloadIGC.php?idSession={flight['flightNumber']}&key={flight['key']}")
        file.write(igc.text)
        file.close()

def getFlightKey(flightNumber) :
    url = f"https://www.syride.com/ficheVol.php?l=fr&idSession={flightNumber}&idActivite=undefined&maxHeight=369"
    page = requests.get(url)
    flightKey = re.search(r'idSession=(\d+)&key=(\d+)', page.text).group(2)
    return flightKey

def getFlightsListUrl(spot_id, page_number) :
    return f"https://www.syride.com/scripts/ajx_vols.php?l=fr&idPays={ID_PAYS}&idSpot={spot_id}&page={page_number}&order=distance&tri=DESC"
