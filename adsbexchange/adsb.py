from .connection.serverconnection import ServerConnection
from .persistence.airspace import Airspace

refresh_miliseconds = -1
tracked_regions = []


class Adsbexchange:
    def __init__(self, start: bool) -> None:
        if start:
            self.conn = ServerConnection()

    def fetch_region():
        pass


if __name__ == "__main__":
    adsb = Adsbexchange(start=True)
    adsb.conn.fetch_tiles(indexes=['5988'])
