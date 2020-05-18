'''
Coordinate with latitude and longitude.
'''
class Coordinate:
    '''
    Constructor.
    '''
    def __init__(self, lat, long):
        self.latitude = lat
        self.longitude = long

    
    def __str__(self):
        return "{ latitude: " + str(self.latitude) + ", longitude: " + str(self.longitude) + " }"


'''
Minimal class representing a nearby place.
'''
class NearbyPlace:
    '''
    Constructor.
    '''
    def __init__(self, name, place_id, types, lat=0, long=0):
        self.name = name
        self.place_id = place_id
        self.types = types
        self.coordinate = Coordinate(lat, long)
    
    def __str__(self):
        return "{ name: '" + self.name + "', place_id: '" + self.place_id \
            + "', types: " + str(self.types) + ", coordinate: " + str(self.coordinate) + " }"
