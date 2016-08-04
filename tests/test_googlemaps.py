import os
from server.app.googlemapsAtoB import GoogleMapsAtoB

API_KEY = os.environ.get("API_KEY")

print(API_KEY)

gmaps1 = GoogleMapsAtoB("I Ferry Building San Francisco Landmark \
    Building, San Francisco, CA 94111", "1600 Amphitheatre Pkwy, \
    Mountain View, CA 94043", api_key=API_KEY)

def test_distance():
    assert gmaps1.get_distance() == 36.7

def test_time():
    assert gmaps1.get_time() == 46.0
