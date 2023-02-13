import aerofiles
import pandas as pd
import numpy as np
import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


class FilterIgc :

    def __init__(self, inputDir):
        self.inputDir = inputDir

    def filter(self) :
        for igcFile in Path(input_dir).glob('*'):
            with open(igcFile, "r") as f:
                decoded_igc = aerofiles.igc.Reader().read(f.readlines())
            
            latitudes = np.array([record['lat'] for record in decoded_igc['fix_records'][1]])
            longitudes = np.array([record['lon'] for record in decoded_igc['fix_records'][1]])
            altitudes= np.array([record['gps_alt'] for record in decoded_igc['fix_records'][1]])
            dates = np.array([record['time'] for record in decoded_igc['fix_records'][1]])
    
            timestamps = np.array([datetime.datetime.combine(datetime.date(2020,1,1), time) for time in dates])
            differences = np.diff(timestamps)
            vfunc = np.vectorize(lambda x: x.total_seconds())
            delta = vfunc(differences).astype(int)
    
            lat1 = np.array(latitudes)
            lat2 = lat1[1:]
            lat1 = lat1[0:-1]
            long1 = np.array(longitudes)
            long2 = long1[1:]
            long1 = long1[0:-1]
    
            km = haversine_np(long1,lat1,long2,lat2)
            v = (km / delta) * 3600
            indexOfDirection = direction(lat1, long1, lat2, long2)
            vfunc = np.vectorize(getDirection)
            directions = vfunc(indexOfDirection)
            df = pd.DataFrame({'vitesse': v, 'direction': directions, 'km': km, 'delta': delta, 'timestamps': timestamps[1:], 'altitude': altitudes[1:], 'latitude': latitudes[1:], 'longitude': longitudes[1:]})
            distanceFromTakeOf = int(haversine_np(df['longitude'].iloc[0], df['latitude'].iloc[0], df['longitude'].iloc[-1], df['latitude'].iloc[-1]) * 1000)
    
            if distanceFromTakeOf > distance_min_between_takeoff_and_landing :
                logger.debug(f"Flight by {igcFile} a été a plus de {distance_min_between_takeoff_and_landing}m de la comté. Exactement {distanceFromTakeOf}m")
            else :
                logger.debug(f"Et c'est le fail, {distanceFromTakeOf}m de la comté")
    
def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

def direction(lat1, lon1, lat2, lon2):
    dLon = lon2 - lon1
    y = np.sin(dLon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dLon)
    brng = np.arctan2(y, x)
    brng = np.degrees(brng)
    brng = (brng + 360) % 360
    brng = 360 - brng # count degrees counter-clockwise - remove to make clockwise
    index = ((brng + 11.25) / 22.5).astype(int) % 16
    return index

def getDirection(x):
    return ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"][x]

def passedNearPoint(df, longitude, latitude, distance): 
    tempDf = df.iloc[::60, :].copy() # ne garder qu'un point toute les 60 secondes pour optimiser
    tempDf['distanceFromPoint'] = (haversine_np(tempDf['longitude'], tempDf['latitude'], longitude , latitude) * 1000).astype(int)
    tempDf['isNearPoint'] = tempDf['distanceFromPoint'] < distance
    return len(tempDf[tempDf['isNearPoint']]) > 0
