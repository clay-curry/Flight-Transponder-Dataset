from re import L
from time import sleep
from typing import List
from aircraft import Aircraft
import regex as rx
import requests as re
from logging import basicConfig, DEBUG, debug, info, warning

server_URL = 'https://globe.adsbexchange.com'
# current time (ms, since 1970)
header_conf = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "if-none-match": "\"620589bd-21b8\"",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


class ServerConnection:
    """Establishes a connection with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """

    def __init__(self):
        self.s = re.Session()
        self.s.headers = header_conf
        self.s.headers['cookie'] = self.make_cookie()

        self.index_html = self.s.get(server_URL)
        debug(f'{server_URL} returned with status {self.index_html.status_code}')
        if self.index_html.status_code >= 400:
            raise re.ConnectionError(
                f"ServerConnection object could not connect to {server_URL}")

    def make_cookie(self):
        debug("making new cookie")
        from time import time
        from random import choices
        from string import ascii_lowercase
        from urllib3.exceptions import HeaderParsingError
        sumbit_time_ms = int(time() * 1000)

        cookie_expire = str(sumbit_time_ms + 2*86400*1000)  # two days
        cookie_token = '_' + \
            ''.join(choices(ascii_lowercase + '1234567890', k=11))
        cookie = 'adsbx_sid=' + cookie_expire + cookie_token

        new_cookie_head = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "cookie":   cookie,
            "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        submit_cookie_to = server_URL + \
            '/globeRates.json?_=' + str(sumbit_time_ms)
        try:
            r = re.get(submit_cookie_to, headers=new_cookie_head)
        except HeaderParsingError:
            debug(f'{submit_cookie_to} caused a HeaderParsingError (this is normal)')

        return cookie

    def fetch_tile(self, index: str) -> re.models.Response:
        data_prefix = '/data/globe_'
        data_suffix = '.binCraft'
        r = self.s.get(server_URL + data_prefix + index + data_suffix)
        if r.status_code >= 400:
            warning(
                f'fetch_time{ index } returned with status code {r.status_code}. Trying again with a new cookie in 3 seconds.')
            self.s.headers['cookie'] = self.make_cookie()
            sleep(3)
            r = self.s.get(server_URL + data_prefix + index + data_suffix)
            if r.status_code >= 400:
                raise re.ConnectionError(
                    f"ServerConnection object could not connect to {server_URL}")
        return r

    def pull_tiles(self, indexes: List[str]) -> List[Aircraft]:
        crafts = []
        for index in indexes:
            r = self.fetch_tile(index)
            crafts.extend(self.decode_response(r))
            sleep(2)
        return crafts

    def decode_response(self, data: re.models.Response) -> List[Aircraft]:
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
        debug(f'len(data) = {len(data)}')
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

        debug(f'now = {now}')
        debug(f'stride = {stride}')
        debug(f'global_ac_count_withpos = {global_ac_count_withpos}')
        debug(f'globeIndex = {globeIndex}')
        debug(f'south = {south}')
        debug(f'west = {west}')
        debug(f'north = {north}')
        debug(f'east = {east}')
        debug(f'messages = {messages}')

        # 1. The allows for types to be encapsulated
        aircraft = []
        for off in range(stride, len(data), stride):
            ac = Aircraft()
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
            if ac.nogps:
                u8[73] |= 64
                u8[73] |= 16

            # must come after the stuff above (validity bits)

            ac.nic_baro = (u8[73] & 1)
            ac.alert1 = (u8[73] & 2)
            ac.spi = (u8[73] & 4)
            ac.flight = ac.flight if (u8[73] & 8) else None
            ac.alt_baro = ac.alt_baro if (u8[73] & 16) else None
            ac.alt_geom = ac.alt_geom if (u8[73] & 32) else None

            ac.lat = ac.lat if (u8[73] & 64) else None
            ac.lon = ac.lon if (u8[73] & 64) else None
            ac.seen_pos = ac.seen_pos if (u8[73] & 64) else None

            ac.gs = ac.gs if (u8[73] & 128) else None

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

            if ac.airground == 1:
                ac.alt_baro = "ground"

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

            aircraft.append(ac)

        return aircraft


"""
def get_map_info(conn):
    global server_URL
    # retrieve attributes needed to find map tiles
    lib_URL_pattern = rx.compile(r'libs_.*?\.js')
    map_attributes_pattern = rx.compile(
        r"(?<=let data = JSON.parse\('){.*?}(?='\);)")

    lib_URL = lib_URL_pattern.search(conn.index_html.text).group(0)
    map_attributes = map_attributes_pattern.search(
        re.get(server_URL + lib_URL).text).group(0)
    from json import loads
    attributes = loads(map_attributes)
    from adsbexchange import refresh_miliseconds
    refresh_miliseconds = attributes['refresh']
    from region import globeIndexGrid, globeIndexSpecialTiles
    globeIndexGrid = attributes['globeIndexGrid']
    globeIndexSpecialTiles = attributes['globeIndexSpecialTiles']
"""

if __name__ == "__main__":
    import time
    basicConfig(format="%(message)s", level=DEBUG)

    tic = time.perf_counter()
    conn = ServerConnection()
    toc = time.perf_counter()
    print(f"created Connection object in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    r = conn.fetch_tile("5988")
    toc = time.perf_counter()
    print(f"fetched tile in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    acl = conn.decode_response(r)
    toc = time.perf_counter()
    print(f"decoded response in {toc - tic:0.4f} seconds")

    print(f'NUMBER PLANES = {len(acl)}')
    print(f'string example: {acl[0].to_list()}')
    print(f'dict example: {acl[0].to_dict()}')
    print(f'response = {[(ac.hex, ac.lat, ac.lon, len(ac)) for ac in acl]}')
