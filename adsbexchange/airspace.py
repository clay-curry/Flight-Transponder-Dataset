import math

class Airspace():
    def __init__(self, lat, lon, radius):
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.tile_indexes = globe_indexes()



    def update_region():
        # 


# number of lat, long divisions per tile
globeIndexGrid = 3
globeIndexSpecialTiles = {}
globeIndexCached = {}


# Distances are measured in miles.
# Longitudes and latitudes are measured in degrees.
# Earth is assumed to be perfectly spherical.

earth_radius = 3960.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi

def change_in_latitude(miles):
    "Given a distance north, return the change in latitude."
    return (miles/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, miles):
    "Given a latitude and a distance west, return the change in longitude."
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (miles/r)*radians_to_degrees




def globe_indexes(region) -> List[str]:
    """ accepts a Region, returns indexes of all "grid tiles" covering this region."""
    north_bound = region.lat + change_in_latitude(region.)
    south_bound = = region.lat + change_in_latitude(region.lat)
    east_bound
    west_bound
    
    
    north_bound = lat + rad/69.0 if lat + rad/69.0 < 89.5 else 89.5
    south_bound = lat - rad/69.0 if lat - rad/69.0 > -89.5 else -89.5
    east_bound = lon + rad/54.6 if lon + rad/54.6 < 179 else 179
    west_bound = lon - rad/54.6 if lon - rad/54.6 > -179 else -179

def globe_index(lat, lon):
    grid = globeIndexGrid

    lat = grid * math.floor((lat + 90) / grid) - 90
    lon = grid * math.floor((lon + 180) / grid) - 180
    print(lat)
    print(lon)

    i = math.floor((lat + 90) / grid)
    j = math.floor((lon + 180) / grid)

    lat_multiplier = math.floor(360 / grid + 1)
    defaultIndex = i * lat_multiplier + j + 1000
    index = -1
    try:
        index = globeIndexCached[f"{defaultIndex}"]
        return index

    except KeyError:
        # not yet in lookup, check special tiles
        for i in range(len(globeIndexSpecialTiles)):
            tile = globeIndexSpecialTiles[i]
            if (lat >= tile[0] and lat < tile[2]) and ((tile[1] < tile[3] and lon >= tile[1] and lon < tile[3]) or tile[1] > tile[3] and (lon >= tile[1] or lon < tile[3])):
                globeIndexCached[f"{defaultIndex}"] = index = i
        if index == -1:
            globeIndexCached[f"{defaultIndex}"] = index = defaultIndex
        return index



if __name__ == "__main__":
    from serverconnection import ServerConnection
    ServerConnection()
    print(globe_index(35.222569, -97.439476))
