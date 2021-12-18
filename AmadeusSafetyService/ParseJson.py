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