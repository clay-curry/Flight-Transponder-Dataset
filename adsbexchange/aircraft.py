from typing import Dict


class Aircraft:
    def __init__(self):
        self.hex = None
        self.seen_pos = None
        self.seen_pos = None
        self.seen = None

        self.lon = None
        self.lat = None

        self.baro_rate = None
        self.geom_rate = None
        self.alt_baro = None
        self.alt_geom = None

        self.nav_altitude_mcp = None
        self.nav_altitude_fms = None
        self.nav_qnh = None
        self.nav_heading = None

        self.squawk = None
        self.gs = None
        self.mach = None
        self.roll = None

        self.track = None
        self.track_rate = None
        self.mag_heading = None
        self.true_heading = None

        self.wd = None
        self.ws = None
        self.oat = None
        self.tat = None

        self.tas = None
        self.ias = None
        self.rc = None
        self.messages = None

        self.category = None
        self.nic = None

        self.nav_modes = None
        self.emergency = None
        self.type = None

        self.airground = None
        self.nav_altitude_src = None

        self.sil_type = None
        self.adsb_version = None
        self.adsr_version = None
        self.tisb_version = None

        self.nac_p = None
        self.nac_v = None

        self.sil = None
        self.gva = None
        self.sda = None
        self.nic_a = None
        self.nic_c = None

        self.flight = None
        self.dbFlags = None
        self.t = None
        self.r = None

        self.receiverCount = None
        self.rssi = None
        self.extraFlags = None
        self.nogps = None

        self.nic_baro = None
        self.alert1 = None
        self.spi = None
        self.calc_track = None
        self.version = None
        self.rId = None

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


if __name__ == "__main__":
    print("Unit Test: Aircraft Class")
    ac = Aircraft()
    print(ac.to_dict())
    print(None)
