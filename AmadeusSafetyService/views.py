from django.shortcuts import render
from amadeus import Client, ResponseError
import requests
from django.http import HttpResponse
import json
from django.shortcuts import render
import math
from . import ParseJson
from django.core.cache import cache
import googlemaps
import hashlib
# Create your views here
def returnGmapsClient():
    gmapsKey = googlemaps.Client(key="")
    return gmapsKey

def covertLatLongToSWNE(latitude,longitude):
    maxLatitude, maxLongitude =  kmInDegree(latitude, longitude)
    north = latitude + maxLatitude
    south = latitude - maxLatitude
    east = longitude + maxLongitude
    west = longitude - maxLongitude
    return [north, west, south, east]

def setGetCache(cacheKey):
    amadeus = Client(
        client_id="",
        client_secret="",
        log_level='debug'
    )
    cacheTime = 86000
    cachedReq = cache.get(cacheKey)
    if not cachedReq:
        print("Request not found in the cache")
        responseUsingLatitude = amadeus.safety.safety_rated_locations.get(latitude= 41.39848388029149, longitude=2.160873)
        if responseUsingLatitude == None:
            return HttpResponse(json.dumps({"error": "Unable to find"}))
        else:
            print(responseUsingLatitude.data)
            cache.set(cacheKey, responseUsingLatitude.data, cacheTime)
            return HttpResponse(ParseJson.returnWomenCrime(responseUsingLatitude.data))
    return HttpResponse(ParseJson.returnWomenCrime(cachedReq))
    

def kmInDegree(lat, long):
    pi = math.pi
    eSq = 0.00669437999014
    a = 6378137.0; 
    lat = lat * pi / 180; 
    long = long * pi / 180; 

    latLength = (pi * a * (1 - eSq)) / (180 * math.pow((1 - eSq * math.pow(math.sin(lat), 2)), 3 / 2))
    longLength = (pi * a * math.cos(long)) / (180 * math.sqrt((1 - (eSq * math.pow(math.sin(long), 2)))))

  #If you want a greater offset, say 5km then change 1000 into 5000
  
    latitude = float(50000 / latLength)
    longitude =float(50000 / longLength)
    return latitude, longitude

def getSafetyRatedLocations(request):
    gmapsKey = returnGmapsClient()

    latitude = float(request.GET.get('latitude'))
    longitude = float(request.GET.get('longitude'))
    northWestSouthEast = covertLatLongToSWNE(latitude, longitude)
    print("My coordinates ")
    print(northWestSouthEast)
    try:
        latitude6f = str(41.39848388029149).encode('utf-8')
        longitude6f = str(2.160873).encode('utf-8')
        cacheKey = hashlib.sha256(latitude6f[0:8] + longitude6f[0:8]).hexdigest()
        return setGetCache(cacheKey)
    except ResponseError as error:
        raise error
