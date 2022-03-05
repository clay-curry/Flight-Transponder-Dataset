from typing import Dict, List

from sqlalchemy import Column, Integer, String

class AircraftWaypoint:
    """E
    """
    def __init__(self):
        self.hex = self.seen_pos = self.seen = None
        self.lon = self.lat = None
        self.baro_rate =self.geom_rate = self.alt_baro = self.alt_geom = None
        self.nav_altitude_mcp = self.nav_altitude_fms = self.nav_qnh = self.nav_heading = None
        self.squawk = self.gs = self.mach = self.roll = None
        self.track = self.track_rate = self.mag_heading = self.true_heading = None
        self.wd = self.ws = self.oat = self.tat = None
        self.tas = self.ias = self.rc = self.messages = None
        self.category = self.nic = None
        self.nav_modes = self.emergency = self.type = None
        self.airground = self.nav_altitude_src = None
        self.sil_type = self.adsb_version = self.adsr_version = self.tisb_version = None
        self.nac_p = self.nac_v = None
        self.sil = self.gva = self.sda = self.nic_a = self.nic_c = None
        self.flight = self.dbFlags = self.t = self.r = None
        self.receiverCount = self.rssi = self.extraFlags = self.nogps = None
        self.nic_baro = self.alert1 = self.spi = self.calc_track = self.version = self.rId = None

    def to_list(self) -> List[str]:
        return [self.hex,
                self.seen_pos,
                self.seen,
                self.lon,
                self.lat,
                self.baro_rate,
                self.geom_rate,
                self.alt_baro,
                self.alt_geom,
                self.nav_altitude_mcp,
                self.nav_altitude_fms,
                self.nav_qnh,
                self.nav_heading,
                self.squawk,
                self.gs,
                self.mach,
                self.roll,
                self.track,
                self.track_rate,
                self.mag_heading,
                self.true_heading,
                self.wd,
                self.ws,
                self.oat,
                self.tat,
                self.tas,
                self.ias,
                self.rc,
                self.messages,
                self.category,
                self.nic,
                self.nav_modes,
                self.emergency,
                self.type,
                self.airground,
                self.nav_altitude_src,
                self.sil_type,
                self.adsb_version,
                self.adsr_version,
                self.tisb_version,
                self.nac_p,
                self.nac_v,
                self.sil,
                self.gva,
                self.sda,
                self.nic_a,
                self.nic_c,
                self.flight,
                self.dbFlags,
                self.t,
                self.r,
                self.receiverCount,
                self.rssi,
                self.extraFlags,
                self.nogps,
                self.nic_baro,
                self.alert1,
                self.spi,
                self.calc_track,
                self.version,
                self.rId]

    def __len__(self):
        return len(str(self.to_list()))

    def to_dict(self) -> Dict[str, str]:
        dic = {}
        for attr in self.__dict__:
            if self.__dict__[attr] is None:
                dic[attr] = None
            else:
                dic[attr] = str(self.__dict__[attr]).upper()
        return dic


if __name__ == "__main__":
    print("Unit Test: Aircraft Class")
    ac = AircraftWaypoint()
    print(ac.__dict__)
    print("TEST")
    print(ac.to_dict())
