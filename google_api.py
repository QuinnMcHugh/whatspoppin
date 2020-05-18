#!/usr/bin/env python3

import requests
import time
import populartimes
from nearby_place import *

'''
Class which handles requests to google API.
'''
class GoogleAPI:

    '''
    Loads API keys.
    '''
    def load_API_keys(self):
        key_file = './api_keys.env'
        with open(key_file) as kf:
            self.keys = eval(kf.read())

    '''
    Core code to ask google for bars in a circle.
    '''
    def get_valid_results(self, search_kind, radius, latitude, longitude):
        latlong = str(latitude) + ',' + str(longitude)
        places = []
        next_page = True
        payload = {"location":latlong, "radius": radius, "type": search_kind, "key":self.keys['google']}

        while next_page:
            r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=payload)
            responses = r.json()
            for result in responses['results']:
                location = result['geometry']['location']
                found_place = NearbyPlace(result['name'], result['place_id'], result['types'],
                                          location['lat'], location['lng'])
                places.append(found_place)
            if 'next_page_token' not in responses:
                next_page = False
            else:
                payload['pagetoken'] = responses['next_page_token']
                time.sleep(2) # short delay ensuring next page is ready

        return places

    '''
    Get a bar's popular times
    '''
    def get_popular_times(self, place_id):
        return populartimes.get_id(self.keys['google'], place_id)


    '''
    Constructor.
    '''
    def __init__(self):
        self.load_API_keys()

if __name__ == "__main__":
    googleAPI = GoogleAPI()
    res = googleAPI.get_valid_results('bar', 1000, 47.620425, -122.349138)
    print(len(res))
    for i in res:
        print(i.name)
