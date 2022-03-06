import imp
from multiprocessing import Process
from typing import List
import requests as re
from multiprocessing import Queue
from ..persistence.aircraftwaypoint import AircraftWaypoint
from time import time

# CPU Bound Process
class AirspaceDecoder(Process):

    def __init__(self, decode_queue: Queue, database_queue: Queue):
        Process.__init__(self)
        self.decode_queue = decode_queue
        self.database_queue = database_queue
               
    def run(self):
        waypoints: List[AircraftWaypoint] = []
        while True:
            requests = self.decode_queue.get(block=True)
            for request in requests:
                waypoints.extend(self.decode_tile(request))
            self.database_queue.put(waypoints)
            waypoints = []

    def decode_tile(self, data: re.models.Response) -> List[AircraftWaypoint]:
        """Function decodes a raw byte stream returned from the adsbexchange.com server into something more meaningful.

        Note that wherever byte transformations seem ambiguous, trust me, they were confusing to me too. This particular
        encoding is proprietary and thus, closed-source. Fortunately, there is minimal ambiguity once decoded.

        You will find that this function is a one-to-one transpiled version of the JS function for decoding messages in
        browser. The server returns attributes of PlaneObjects where attributes are encoded as binary words of various
        byte lengths. The exact details of how attributes are organized and decoded are written as code comments.

        Args:
            data ([type]): raw bytes from the adsbexchange.com server
        """

        import struct
        import math
        data = data.content
        # let vals = new Uint32Array(data.buffer, 0, 8)
        vals = struct.unpack_from('<8I', data, 0)

        now = vals[0] / 1000 + vals[1] * 4294967.296
        stride = vals[2]
        global_ac_count_withpos = vals[3]
        globeIndex = vals[4]
        limits = struct.unpack_from('<4h', data, 20)
        south = limits[0]
        west = limits[1]
        north = limits[2]
        east = limits[3]
        messages = vals[7]

        # 1. The allows for types to be encapsulated
        waypoints = []
        for off in range(stride, len(data), stride):
            ac = AircraftWaypoint()
            u32 = struct.unpack_from(f'<{int(stride/4)}I', data, off)
            s32 = struct.unpack_from(f'<{int(stride/4)}i', data, off)
            u16 = struct.unpack_from(f'<{int(stride/2)}H', data, off)
            s16 = struct.unpack_from(f'<{int(stride/2)}h', data, off)
            u8 = struct.unpack_from(f'<{int(stride)}B', data, off)
            t = s32[0] & (1 << 24)
            ac.hex = f'{(s32[0] & ((1<<24) - 1)):06x}'
            ac.hex = ('~' + ac.hex) if t else ac.hex
            ac.seen_pos = u16[2] / 10
            ac.seen = u16[3] / 10

            ac.lon = s32[2] / 1e6
            ac.lat = s32[3] / 1e6

            ac.baro_rate = s16[8] * 8
            ac.geom_rate = s16[9] * 8
            ac.alt_baro = s16[10] * 25
            ac.alt_geom = s16[11] * 25

            ac.nav_altitude_mcp = u16[12] * 4
            ac.nav_altitude_fms = u16[13] * 4
            ac.nav_qnh = s16[14] / 10
            ac.nav_heading = s16[15] / 90

            ac.squawk = f'{u16[16]:04x}'
            ac.gs = s16[17] / 10
            ac.mach = s16[18] / 1000
            ac.roll = s16[19] / 100

            ac.track = s16[20] / 90
            ac.track_rate = s16[21] / 100
            ac.mag_heading = s16[22] / 90
            ac.true_heading = s16[23] / 90

            ac.wd = s16[24]
            ac.ws = s16[25]
            ac.oat = s16[26]
            ac.tat = s16[27]

            ac.tas = u16[28]
            ac.ias = u16[29]
            ac.rc = u16[30]
            ac.messages = u16[31]

            ac.category = None if not u8[64] else str(hex(int(u8[64]))).upper()
            ac.nic = u8[65]

            nav_modes = u8[66]
            ac.nav_modes = True
            ac.emergency = u8[67] & 15
            ac.type = (u8[67] & 240) >> 4

            ac.airground = u8[68] & 15
            ac.nav_altitude_src = (u8[68] & 240) >> 4

            ac.sil_type = u8[69] & 15
            ac.adsb_version = (u8[69] & 240) >> 4

            ac.adsr_version = u8[70] & 15
            ac.tisb_version = (u8[70] & 240) >> 4

            ac.nac_p = u8[71] & 15
            ac.nac_v = (u8[71] & 240) >> 4

            ac.sil = u8[72] & 3
            ac.gva = (u8[72] & 12) >> 2
            ac.sda = (u8[72] & 48) >> 4
            ac.nic_a = (u8[72] & 64) >> 6
            ac.nic_c = (u8[72] & 128) >> 7

            ac.flight = ""
            for i in range(78, 86):
                if not u8[i]:
                    break
                ac.flight += chr(u8[i])

            ac.dbFlags = u16[43]

            ac.t = ""
            for i in range(88, 92):
                if not u8[i]:
                    break
                ac.t += chr(u8[i])

            ac.r = ""
            for i in range(92, 104):
                if not u8[i]:
                    break
                ac.r += chr(u8[i])

            ac.receiverCount = u8[104]

            ac.rssi = 10 * math.log(u8[105] * u8[105] / 65025 + 1.125e-5, 10)

            ac.extraFlags = u8[106]
            ac.nogps = ac.extraFlags and 1
            gps = u8[73]
            if ac.nogps:
                gps |= 64
                gps |= 16

            # must come after the stuff above (validity bits)

            ac.nic_baro = (gps & 1)
            ac.alert1 = (gps & 2)
            ac.spi = (gps & 4)
            ac.flight = ac.flight if (gps & 8) else None
            ac.alt_baro = ac.alt_baro if (gps & 16) else None
            ac.alt_geom = ac.alt_geom if (gps & 32) else None

            ac.lat = ac.lat if (gps & 64) else None
            ac.lon = ac.lon if (gps & 64) else None
            ac.seen_pos = ac.seen_pos if (gps & 64) else None

            ac.gs = ac.gs if (gps & 128) else None

            ac.ias = ac.ias if (u8[74] & 1) else None
            ac.tas = ac.tas if (u8[74] & 2) else None
            ac.mach = ac.mach if (u8[74] & 4) else None
            ac.track = ac.track if (u8[74] & 8) else None
            ac.calc_track = ac.track if not (u8[74] & 8) else None
            ac.track_rate = ac.track_rate if (u8[74] & 16) else None
            ac.roll = ac.roll if (u8[74] & 32) else None
            ac.mag_heading = ac.mag_heading if (u8[74] & 64) else None
            ac.true_heading = ac.true_heading if (u8[74] & 128) else None

            ac.baro_rate = ac.baro_rate if (u8[75] & 1) else None
            ac.geom_rate = ac.geom_rate if (u8[75] & 2) else None
            ac.nic_a = ac.nic_a if (u8[75] & 4) else None
            ac.nic_c = ac.nic_c if (u8[75] & 8) else None
            ac.nic_baro = ac.nic_baro if (u8[75] & 16) else None
            ac.nac_p = ac.nac_p if (u8[75] & 32) else None
            ac.nac_v = ac.nac_v if (u8[75] & 64) else None
            ac.sil = ac.sil if (u8[75] & 128) else None

            ac.gva = ac.gva if (u8[76] & 1) else None
            ac.sda = ac.sda if (u8[76] & 2) else None
            ac.squawk = ac.squawk if (u8[76] & 4) else None
            ac.emergency = ac.emergency if (u8[76] & 8) else None
            ac.spi = ac.spi if (u8[76] & 16) else None
            ac.nav_qnh = ac.nav_qnh if (u8[76] & 32) else None
            ac.nav_altitude_mcp = ac.nav_altitude_mcp if (
                u8[76] & 64) else None
            ac.nav_altitude_fms = ac.nav_altitude_fms if (
                u8[76] & 128) else None

            ac.nav_altitude_src = ac.nav_altitude_src if (u8[77] & 1) else None
            ac.nav_heading = ac.nav_heading if (u8[77] & 2) else None
            ac.nav_modes = ac.nav_modes if (u8[77] & 4) else None
            ac.alert1 = ac.alert1 if (u8[77] & 8) else None
            ac.ws = ac.ws if (u8[77] & 16) else None
            ac.wd = ac.wd if (u8[77] & 16) else None
            ac.oat = ac.oat if (u8[77] & 32) else None
            ac.tat = ac.tat if (u8[77] & 32) else None

            #if ac.airground == 1:
             #   ac.alt_baro = "ground"

            if (ac.nav_modes):
                ac.nav_modes = []
                if (nav_modes & 1):
                    ac.nav_modes.append('autopilot')
                if (nav_modes & 2):
                    ac.nav_modes.append('vnav')
                if (nav_modes & 4):
                    ac.nav_modes.append('alt_hold')
                if (nav_modes & 8):
                    ac.nav_modes.append('approach')
                if (nav_modes & 16):
                    ac.nav_modes.append('lnav')
                if (nav_modes & 32):
                    ac.nav_modes.append('tcas')

            if ac.type == 0:
                ac.type = 'adsb_icao'
            elif ac.type == 1:
                ac.type = 'adsb_icao_nt'
            elif ac.type == 2:
                ac.type = 'adsr_icao'
            elif ac.type == 3:
                ac.type = 'tisb_icao'
            elif ac.type == 4:
                ac.type = 'adsc'
            elif ac.type == 5:
                ac.type = 'mlat'
            elif ac.type == 6:
                ac.type = 'other'
            elif ac.type == 7:
                ac.type = 'mode_s'
            elif ac.type == 8:
                ac.type = 'adsb_other'
            elif ac.type == 9:
                ac.type = 'adsr_other'
            elif ac.type == 10:
                ac.type = 'tisb_trackfile'
            elif ac.type == 11:
                ac.type = 'tisb_other'
            elif ac.type == 12:
                ac.type = 'mode_ac'
            else:
                ac.type = 'unknown'

            type4 = ac.type[0:4]
            if (type4 == 'adsb'):
                ac.version = ac.adsb_version
            elif (type4 == 'adsr'):
                ac.version = ac.adsr_version
            elif (type4 == 'tisb'):
                ac.version = ac.tisb_version

            if (stride == 112):
                part2 = f'{u32[27]:08x}'
                ac.rId = part2[0:4] + '-' + part2[4]

            if ac.seen is not None:
                ac.seen = time() - ac.seen
            if ac.seen_pos is not None:
                ac.seen_pos = time() - ac.seen_pos
            
            waypoints.append(ac)

        return waypoints


if __name__ == "__main__":
    pass
