"""
A simple GoogleMaps API wrapper.

Necessary steps:
1. Get a Google Maps API key here: https://developers.google.com/maps/documentation/static-maps/
2. Include the API key in the constructor or assign it as an environment variable.
3. Let A be the starting point (an address or (lat, long)) and B be the destination.
Then create a GoogleMapsAtoB object (e.g. g = GoogleMapsAtoB(A, B))
4. Get distance from A to B using the 'get_distance' method and the time using the
'get_time' method.
"""

import googlemaps as gm
from datetime import datetime

class GoogleMapsAtoB:
    def __init__(self, src, dst, api_key, mode='driving'):
        self.client = gm.Client(api_key)
        self.directions = self.client.directions(origin=src, destination=dst, \
            mode=mode, departure_time=datetime.now())

    def get_distance(self):
        return float(self.directions[0]["legs"][0]["distance"]["text"].split(" ")[0])

    def get_time(self):
        return float(self.directions[0]["legs"][0]["duration"]["text"].split(" ")[0])
