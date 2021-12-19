import json
def returnJsonMapOfCrimes(jsonResponse):
    data = jsonResponse
    dictOfLatLong = {}
    for i in range(0,len(data)):
        dictOfLatLong[data[i]["id"]] = {"latitude": data[i]["geoCode"]["latitude"],
        "longitude": data[i]["geoCode"]["longitude"],
        "name": data[i]["name"],
        "overall":  data[i]["safetyScores"]["overall"],
        "womenSafety": data[i]["safetyScores"]["women"],
        "lgbtq": data[i]["safetyScores"]["lgbtq"],
        "medical": data[i]["safetyScores"]["medical"],
        "physicalHarm": data[i]["safetyScores"]["physicalHarm"],
        "politicalFreedom": data[i]["safetyScores"]["politicalFreedom"],
        "theft": data[i]["safetyScores"]["theft"]
        }
    return json.dumps(dictOfLatLong)


def getIata(bannedArea):
    return bannedArea['iataCode']

def getBannedCountries(covidJsonResponse, currentCountryCode):
    bannedCountriesArea= covidJsonResponse["areaAccessRestriction"]["entry"]["bannedArea"]
    bannedCountriesAreaIataCode = list(map(getIata, bannedCountriesArea))
    count = 0
    for countryCode in bannedCountriesAreaIataCode:
        if(countryCode==currentCountryCode):
            count = count + 1
    if count > 0:
        return False, bannedCountriesAreaIataCode
    else:
        return True, bannedCountriesAreaIataCode

def ifNotBannedViewInfo(responseJson, longitude, latitude, toWhichCountry):
    visitingLocationCovidInfo = {}
    visitingLocationCovidInfo['summary'] = responseJson['summary']
    visitingLocationCovidInfo['testing'] = responseJson['areaAccessRestriction']['diseaseTesting']['text']
    if responseJson['diseaseRiskLevel'] == "Extreme":
        visitingLocationCovidInfo['diseaseRiskLevel'] = '<p class="text-danger"><strong>' + 'Disease Risk Level: ' + responseJson['diseaseRiskLevel'] + '</strong></p>'
    elif responseJson['diseaseRiskLevel'] == "High":
        visitingLocationCovidInfo['diseaseRiskLevel'] = '<p class="text-warning"><strong>' + 'Disease Risk Level: ' + responseJson['diseaseRiskLevel'] + '</strong></p>'
    else:
        visitingLocationCovidInfo['diseaseRiskLevel'] = '<p class="text-sucess"><strong>' + 'Disease Risk Level: ' + responseJson['diseaseRiskLevel'] + '</strong></p>'
    
    confirmed = str(responseJson['diseaseCases']['confirmed']) 
    deaths =  str(responseJson['diseaseCases']['deaths'])
    visitingLocationCovidInfo['caseConfirmed'] = '<p><strong>Disease Case Confirmed: ' + confirmed + ' deaths: ' + deaths + '</strong></p>'

    visitingLocationCovidInfo["longitude"] = longitude
    visitingLocationCovidInfo["latitude"] = latitude
    visitingHotspot = False
    toWhichCountry = toWhichCountry.lower()
    print(toWhichCountry)
    country= responseJson['hotspots'].lstrip("<p>")
    country = country.rstrip("</p>").strip('.').lower()
    country = country.split(",")
    print(country)
    for city in country:
        city = city.rstrip(" ")
        city = city.lstrip(" ")
        if toWhichCountry.find(city.lower()) != -1:
            visitingLocationCovidInfo['hotspots'] = '<p class="text-danger"><strong>' + 'You are travelling to one of the hotspots ' + city.upper()+ '</strong></p>'
            visitingLocationCovidInfo["hotspots"] += '<p color="black">' + 'Hotspots are: ' + responseJson['hotspots'] + '</p>'
            visitingHotspot = True
            
    if not visitingHotspot:
        visitingLocationCovidInfo["hotspots"] = '<p color="black"' + 'You are not visiting any hotspots, hotspots are: ' + responseJson['hotspots'] + '</p>'


    return json.dumps(visitingLocationCovidInfo)