from django.shortcuts import render
from amadeus import Client, ResponseError
import requests
from django.http import HttpResponse
import json
from django.shortcuts import render
import math
from . import ParseJson
# Create your views here.
def covertLatLongToSWNE(latitude,longitude):
    maxLatitude, maxLongitude =  kmInDegree(latitude, longitude)
    north = latitude + maxLatitude
    south = latitude - maxLatitude
    east = longitude + maxLongitude
    west = longitude - maxLongitude
    return [north, west, south, east]

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
    amadeus = Client(
        client_id="",
        client_secret="",
        log_level='debug'

    )
    latitude = float(request.GET.get('latitude'))
    longitude = float(request.GET.get('longitude'))
    northWestSouthEast = covertLatLongToSWNE(latitude, longitude)
    print("My coordinates ")
    print(northWestSouthEast)
    try:
        response =  amadeus.safety.safety_rated_locations.by_square.get(
            north=northWestSouthEast[0],
            west=northWestSouthEast[1],
            south=northWestSouthEast[2],
            east=northWestSouthEast[3]
        )
        if response.data == None:
            responseUsingLatitude = amadeus.safety.safety_rated_locations.get(latitude=41.397158, longitude=2.160873)
            if responseUsingLatitude == None:
                return HttpResponse(json.dumps({"error": "Unable to find"}))
            else:
                print(responseUsingLatitude.data)
                return HttpResponse(ParseJson.returnWomenCrime(responseUsingLatitude.data))
        else:
            return HttpResponse(ParseJson.returnWomenCrime(responseUsingLatitude.data))
    except ResponseError as error:
        raise error
