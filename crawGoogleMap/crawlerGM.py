#map api KEY AIzaSyCOlzxW3ZGAtq5u3LD8oeWEsu8mWQpA-tw

from urllib import request
import pandas as pd
from random import randint
from random import shuffle
import json
import numpy as np
from datetime import datetime
import os

from itertools import combinations
from multiprocessing import Pool


GMURL = "https://maps.googleapis.com/maps/api/directions/json?"


df = pd.read_csv('SiloZones_Centroid_Excel.csv')

resrecords = {
    'origin':[],
    'destination':[],
    'duration':[],
    'length':[]
}

LATCOL = "Lat"
LONGCOL = 'Long'
ZONECOL = 'SA1_7DIG11'


df.index = df[ZONECOL]

def req(url):
    res  = request.urlopen(url)
    return json.loads(res.read().decode('gbk'))

def compose_url(parameters):
    url = GMURL
    parastr = list(map(lambda key: key+'='+parameters[key], parameters))
    url = url + '&'.join(parastr)
    return url

def assignLocation(atrip):
    paramap = {
    'origin':'',
    'destination':'',
    'key':'AIzaSyCOlzxW3ZGAtq5u3LD8oeWEsu8mWQpA-tw',
    'mode':'driving',
    'alternatives':'false',
    'unit':'metric',
    'departure_time':'now',
    }
    atrip = list(map(int, atrip))
    originLat = df.at[atrip[0],LATCOL]
    originLong  = df.at[atrip[0],LONGCOL]
    destinationLat = df.at[atrip[1],LATCOL]
    destinationLong = df.at[atrip[1],LONGCOL]
    originLat,originLong, destinationLat, destinationLong
    paramap['origin'] = str(originLat)+','+str(originLong)
    paramap['destination'] = str(destinationLat)+','+str(destinationLong)
    return paramap

def random_get_trip():
    maxIndex = df.shape[0] -1
    while True:
        originrow = str(randint(0,maxIndex))
        destrow = str(randint(0,maxIndex))
        curtrip = [originrow,destrow]
        originZone = str(df.at[curtrip[0],ZONECOL])
        destZone = str(df.at[curtrip[1],ZONECOL])
        if (originrow != destrow) and ((originZone, destZone) in remaining_zones):
            return curtrip

def get_target_trip(zones):
    zonorigin = int(df[df[ZONECOL]==zones[0]].index[0])
    zondest = int(df[df[ZONECOL]==zones[1]].index[0])
    return [zonorigin,zondest]

def get_remaining_zones():
    zonelist = map(str,list(df[ZONECOL]))
    allzones = list(combinations(zonelist,2))
    # print(remaining_zones)
    existingZones =  map(lambda ajson: tuple(ajson.split('_')) ,os.listdir('./jsons'))
    remaining_zones = [x for x in allzones if x not in existingZones]
    print('Remaining',len(remaining_zones),'to process')
    return remaining_zones

def record(resobj,zones):
    originZone = zones[0]
    destZone = zones[1]
    fname = str(originZone)+'_' + str(destZone) +'.json'
    path = './jsons/' + fname
    with open(path,'w') as f:
        json.dump(resobj, f)
    print('get',originZone,destZone)

def parse_json_folder():
    for ajson in os.listdir('./jsons'):
        with open('./jsons/' + ajson,'r') as f:
            resobj = json.load(f)
            zones = ajson[:-5].split('_')
            originZone = zones[0]
            destZone = zones[1]
            leglist = resobj['routes'][0]['legs']
            if len(leglist) is not 1:
                print(originZone, destZone)
                continue
            length = leglist[0]['distance']['value']
            duration = leglist[0]['duration']['value']
            resrecords['origin'].append(originZone)
            resrecords['destination'].append(destZone)
            resrecords['duration'].append(duration)
            resrecords['length'].append(length)

def save_to_csv():
    resrecords['duration(min)'] = np.array(resrecords['duration'])/60
    resdf = pd.DataFrame(resrecords)
    print(resdf)
    resdf.sort_values(['origin','destination'])
    resdf.to_csv('./SA1TravelTime3.csv',index=False)

def get_one_route(zones):
    parameters = assignLocation(zones)
    url = compose_url(parameters)
    resobj = req(url)
    record(resobj,zones)
    return 0

def main():
    remaining_zones = get_remaining_zones()
    shuffle(remaining_zones)
    print(df)
    # pool = Pool(20)
    # res = pool.map(get_one_route,remaining_zones)
    # pool.close()
    # pool.join()
    parse_json_folder()
    save_to_csv()

if __name__ == '__main__':
    main()