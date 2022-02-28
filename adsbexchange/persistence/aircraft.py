from typing import Dict, List


class Aircraft:
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
        return {
            'hex': str(self.hex),
            'seen_pos': str(self.seen_pos),
            'seen_pos': str(self.seen_pos),
            'seen': str(self.seen),
            'lon': str(self.lon),
            'lat': str(self.lat),
            'baro_rate': str(self.baro_rate),
            'geom_rate': str(self.geom_rate),
            'alt_baro': str(self.alt_baro),
            'alt_geom': str(self.alt_geom),
            'nav_altitude_mcp': str(self.nav_altitude_mcp),
            'nav_altitude_fms': str(self.nav_altitude_fms),
            'nav_qnh': str(self.nav_qnh),
            'nav_heading': str(self.nav_heading),
            'squawk': str(self.squawk),
            'gs': str(self.gs),
            'mach': str(self.mach),
            'roll': str(self.roll),
            'track': str(self.track),
            'track_rate': str(self.track_rate),
            'mag_heading': str(self.mag_heading),
            'true_heading': str(self.true_heading),
            'wd': str(self.wd),
            'ws': str(self.ws),
            'oat': str(self.oat),
            'tat': str(self.tat),
            'tas': str(self.tas),
            'ias': str(self.ias),
            'rc': str(self.rc),
            'messages': str(self.messages),
            'category': str(self.category),
            'nic': str(self.nic),
            'nav_modes': str(self.nav_modes),
            'emergency': str(self.emergency),
            'type': str(self.type),
            'airground': str(self.airground),
            'nav_altitude_src': str(self.nav_altitude_src),
            'sil_type': str(self.sil_type),
            'adsb_version': str(self.adsb_version),
            'adsr_version': str(self.adsr_version),
            'tisb_version': str(self.tisb_version),
            'nac_p': str(self.nac_p),
            'nac_v': str(self.nac_v),
            'sil': str(self.sil),
            'gva': str(self.gva),
            'sda': str(self.sda),
            'nic_a': str(self.nic_a),
            'nic_c': str(self.nic_c),
            'flight': str(self.flight),
            'dbFlags': str(self.dbFlags),
            't': str(self.t),
            'r': str(self.r),
            'receiverCount': str(self.receiverCount),
            'rssi': str(self.rssi),
            'extraFlags': str(self.extraFlags),
            'nogps': str(self.nogps),
            'nic_baro': str(self.nic_baro),
            'alert1': str(self.alert1),
            'spi': str(self.spi),
            'calc_track': str(self.calc_track),
            'version': str(self.version),
            'rId': str(self.rId),
        }

    def __str__(self):
        return str(self.to_dict())


if __name__ == "__main__":
    print("Unit Test: Aircraft Class")
    ac = Aircraft()
    print(ac)
