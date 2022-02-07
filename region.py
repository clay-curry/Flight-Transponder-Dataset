import math

# number of lat, long divisions per tile
globeIndexGrid = -1
globeIndexSpecialTiles = {}
globeIndexCached = {}


def globeIndexes(region):
    """ accepts a Region, returns indexes of all "grid tiles" covering this region."""
    lat = grid * math.floor((region.lat + 90) / grid) - \
        90   # lat ∈ [-90, 90] (south to north)    1° lat = 69 miles
    # lon ∈ (-180, 180) (west to east)    1° lon = 54.6 miles
    lon = grid * math.floor((region.lon + 180) / grid) - 180
    rad = region.rad  # mi, rad ∈ (0,1500)


def globe_index(lat, lon):
    # lat ∈ [-90, 90] (south to north)    1° lat = 69 miles
    # lon ∈ (-180, 180) (west to east)    1° lon = 54.6 miles

    grid = globeIndexGrid

    lat = grid * math.floor((lat + 90) / grid) - 90
    lon = grid * math.floor((lon + 180) / grid) - 180

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


class Region():
    def __init__(self, lat, lon, rad):
        self.lat = lat
        self.lon = lon
        self.rad = rad
        north_bound = lat + rad/69.0 if lat + rad/69.0 < 89.5 else 89.5
        south_bound = lat - rad/69.0 if lat - rad/69.0 > -89.5 else -89.5
        east_bound = lon + rad/54.6 if lon + rad/54.6 < 179 else 179
        west_bound = lon - rad/54.6 if lon - rad/54.6 > -179 else -179

    def update_region():
        pass


if __name__ == "__main__":
    from serverconnection import ServerConnection
    ServerConnection()
    print(globe_index(35.222569, -97.439476))
