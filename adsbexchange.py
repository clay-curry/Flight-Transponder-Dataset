from serverconnection import ServerConnection
from region import Region
from aircraft import Aircraft
from typing import List


refresh_miliseconds = -1
tracked_regions = []


class Adsbexchange:
    def __init__(self) -> None:
        self.conn = ServerConnection()

    def fetch_region():
        pass


if __name__ == "__main__":
    adsb = Adsbexchange()
    adsb.conn.fetch_tile(index=['5988'])
    