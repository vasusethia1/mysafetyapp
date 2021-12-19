import googlemaps
import hashlib
# Create your views here
def returnGmapsClient():
    gmapsHandler = googlemaps.Client(key="AIzaSyAJ--ce1fXomzvNJCQOaXJEGw-hz3Zrx34")
    return gmapsHandler

def getCacheKey(latitude, longitude, radius):
    longitude6f = str(longitude).encode('utf-8')
    latitude6f = str(latitude).encode('utf-8')
    radius = str(radius).encode('utf-8')
    cacheKey = hashlib.sha256(latitude6f[0:8] + longitude6f[0:8] + radius).hexdigest()
    return cacheKey
def checkInstance(param1, param2):
    if isinstance(param1, type(param2)):
        return True
    else:
        return False