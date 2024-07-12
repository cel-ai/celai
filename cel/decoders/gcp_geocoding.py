import os
from geopy.geocoders import GoogleV3

GOOGLE_GEOCODING_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY")


def googlev3_decode_location(location):
    if not GOOGLE_GEOCODING_API_KEY:
        raise ValueError("GOOGLE_GEOCODING_API_KEY env var is not set")
    
    geolocator = GoogleV3(api_key=GOOGLE_GEOCODING_API_KEY)
    location = geolocator.reverse(location)
    return location.address


if __name__ == "__main__":
    
    location = (40.748817, -73.985428)
    print(googlev3_decode_location(location))


    location = {
        "latitude": -34.391462,
        "longitude": -58.69314
    }
    
    location = (location["latitude"], location["longitude"])
    print(googlev3_decode_location(location))


