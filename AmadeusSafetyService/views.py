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
from geopy.geocoders import Nominatim


def covertLatLongToSWNE(latitude,longitude):
    maxLatitude, maxLongitude =  kmInDegree(latitude, longitude)
    north = latitude + maxLatitude
    south = latitude - maxLatitude
    east = longitude + maxLongitude
    west = longitude - maxLongitude
    return [north, west, south, east]

def setGetCache(cacheKey, latitude, longitude, radius_1):
    amadeus = Client(
        client_id="wVxpkFJGOIEqT7tyOt36W1UxAVx5P7yZ",
        client_secret="ojlJiwRvfwAK7QFu"
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
    latitude = float(request.GET.get('latitude'))
    longitude = float(request.GET.get('longitude'))
    radius =  int(request.GET.get('radius'))
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
    try:
        geoCodeResult=gmapsHandler.geocode(address)
        print(geoCodeResult)
        latitude = geoCodeResult[0]["geometry"]["location"]["lat"]
        longitude = geoCodeResult[0]["geometry"]["location"]["lng"]
        cacheKey = utils.getCacheKey(latitude, longitude, radius)
        return setGetCache(cacheKey, latitude, longitude, radius)
    except ResponseError as error:
        raise error

def getSetCacheForTravelRestrictions(countryCode, fromCountryCode, latitude, longitude, toWhichCountry):
    amadeus = Client(
        client_id="wVxpkFJGOIEqT7tyOt36W1UxAVx5P7yZ",
        client_secret="ojlJiwRvfwAK7QFu"
    )
    cacheTime = 3600
    travelRestrictionResponse = cache.get(countryCode)
    print(countryCode)
    if not travelRestrictionResponse:
  
        travelRestrictionResponse = amadeus.get("/v1/duty-of-care/diseases/covid19-area-report", countryCode = countryCode)
        print(travelRestrictionResponse.data)
        isAllowed, listOfCountriesBanned = ParseJson.getBannedCountries(travelRestrictionResponse.data, fromCountryCode)
        print(listOfCountriesBanned)
        print(isAllowed)
        if type(travelRestrictionResponse.data) == type(None):
            return HttpResponse(json.dumps({"error": "Unable to find the travel restrictions"}))
        else:
            cache.set(countryCode, travelRestrictionResponse.data, cacheTime)
            if isAllowed:
                return HttpResponse(ParseJson.ifNotBannedViewInfo(travelRestrictionResponse, longitude = longitude, latitude = latitude, toWhichCountry = toWhichCountry))
            else:
                return HttpResponse(json.dumps({"error": "Not allowed to travel"}))
        
    else:
   
        isAllowed, listOfCountriesBanned = ParseJson.getBannedCountries(travelRestrictionResponse, fromCountryCode)
        if(utils.checkInstance(travelRestrictionResponse, None)):
            return {"error": "Unable to find the travel restrictions"}
        else:
            if isAllowed:
                return HttpResponse(ParseJson.ifNotBannedViewInfo(travelRestrictionResponse, longitude = longitude, latitude = latitude, toWhichCountry = toWhichCountry))
            else:
                return HttpResponse(json.dumps({"error": "Not allowed to travel"}))
       
        
        

def getSafeTravelLocations(request):
    
    fromWhichCountry = request.GET.get("from")
    toWhichCountry = request.GET.get("to") 
    gmapsHandler = utils.returnGmapsClient()
    try:
        geoCodeResult=gmapsHandler.geocode(toWhichCountry)
        print(geoCodeResult)
        geolocator = Nominatim(user_agent="geoapi")
        latitude = geoCodeResult[0]["geometry"]["location"]["lat"]
        longitude = geoCodeResult[0]["geometry"]["location"]["lng"]
        location = geolocator.reverse(str(latitude)+","+str(longitude))
        address = location.raw['address']
        toCode = str(address.get('country_code'))
        geoCodeResultFrom = gmapsHandler.geocode(fromWhichCountry)
        location = geolocator.reverse(str(geoCodeResultFrom[0]["geometry"]["location"]["lat"])+","+ str(geoCodeResultFrom[0]["geometry"]["location"]["lng"]))
        address = location.raw['address']
        fromCode = str(address.get('country_code'))
        country = str(address.get('country'))

        if utils.checkInstance(geoCodeResult, None):
            return HttpResponse(json.dumps({"error", "Unable to get the country code"}))
        else:
            print(toCode + "," +  fromCode)
            return getSetCacheForTravelRestrictions(toCode.upper(),fromCode.upper(), latitude, longitude, toWhichCountry)
    except ResponseError as error:
        raise error
