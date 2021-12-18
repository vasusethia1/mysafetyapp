from django.shortcuts import render
from amadeus import Client, ResponseError
import requests
from django.http import HttpResponse
import json
from django.shortcuts import render
import math
from . import ParseJson
from django.core.cache import cache
from . import utils


def covertLatLongToSWNE(latitude,longitude):
    maxLatitude, maxLongitude =  kmInDegree(latitude, longitude)
    north = latitude + maxLatitude
    south = latitude - maxLatitude
    east = longitude + maxLongitude
    west = longitude - maxLongitude
    return [north, west, south, east]

def setGetCache(cacheKey, latitude, longitude, radius_1):
    amadeus = Client(
        client_id="",
        client_secret="",
    )
    cacheTime = 86000
    cachedReq = cache.get(cacheKey)
    if not cachedReq:
        print("Request not found in the cache")
        responseUsingLatitude = amadeus.safety.safety_rated_locations.get(latitude= latitude, longitude= longitude, radius = radius_1)
        if  isinstance(responseUsingLatitude.data, type(None)):
            print("Hello World")
            return HttpResponse(json.dumps({"error": "Unable to find"}))
        else:
            print(responseUsingLatitude.data)
            cache.set(cacheKey, responseUsingLatitude.data, cacheTime)
            return HttpResponse(ParseJson.returnJsonMapOfCrimes(responseUsingLatitude.data))
    else:
        if(type(cachedReq) == type(None)):
            return HttpResponse(json.dumps({"error": "Unable to find"}))
        else:
            print("Found a cache hit")
            return HttpResponse(ParseJson.returnJsonMapOfCrimes(cachedReq))
    

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
    gmapsHandler = utils.returnGmapsClient()

    latitude = float(request.GET.get('latitude'))
    longitude = float(request.GET.get('longitude'))
    radius =  float(request.GET.get('radius'))
    try:
        cacheKey = utils.getCacheKey(latitude, longitude, radius)
        return setGetCache(cacheKey, latitude, longitude, radius)
    except ResponseError as error:
        raise error
def getSafetyLocationFromGivenAddress(request):
    gmapsHandler = utils.returnGmapsClient()
    address = str(request.GET.get('address'))
    radius =  int(request.GET.get('radius'))
    print("address input is: " + address)
    print(radius)
    try:
        geoCodeResult=gmapsHandler.geocode(address)
        print(geoCodeResult)
        latitude = geoCodeResult[0]["geometry"]["location"]["lat"]
        longitude = geoCodeResult[0]["geometry"]["location"]["lng"]
        cacheKey = utils.getCacheKey(latitude, longitude, radius)
        return setGetCache(cacheKey, latitude, longitude, radius)
    except ResponseError as error:
        raise error
        
        
