from typing import List
import requests as re
import gzip
import struct


class ServerConnection:
    """Establishes a connection with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """

    base_URL = 'https://globe.adsbexchange.com'
    data_prefix = '/data/globe_'
    data_sections = ['5987', '5988', '5989']
    data_suffix = '.binCraft'

    header_conf = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "if-none-match": "\"61fa4547-196\"",
        "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "cookie": "_ga=GA1.2.1378886063.1641354185; __gads=ID=bfdb98732c26a741:T=1641579571:S=ALNI_Ma9r3TuDQG9fOvDKu3RlkE3uTY3cA; _gid=GA1.2.1284206835.1643743946; adsbx_sid=1643959800776_8tal59zwez5; cto_bundle=aRIhyF9QdmhsUmxQVXE2RmwyaE1EUGw3czdkbW5FVERXd2UyaEpCWE9LTU41cTAxSE50TFJEU3lmWkN4cFJPNzJFejMlMkZnN1F5JTJGUUFMU1ZrRGNibTBBU3hJQVVuZSUyQm44akJPQnglMkJZOGs3VGJ6R09Ld2hsJTJCVmNUcVl6JTJCSDJIU0klMkJoTFRGMnRXeVl0T2ZtaEw3aFF1ZjBYamczQSUzRCUzRA",
        "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
        "Referrer-Policy": "strict-origin-when-cross-origin"

    }

    def __init__(self) -> None:
        dataurl = 'https://globe.adsbexchange.com/data/globe_5988.binCraft'
        r = re.get(dataurl, headers=ServerConnection.header_conf)
        print(f"response code: {r.status_code}")
        # access the data
        self.decode_response(r.content)

    def decode_response(self, data):
        """decodes raw bytes from the adsbexchange.com server into something more meaningful.

        Args:
            data ([type]): [description]


        """
        # words in 'data' are little-endian (the least-significant byte at the smallest address)
        response_time = struct.unpack('<I', data[0:4])[0] / 1000


if __name__ == "__main__":
    ServerConnection()


""""        
function decode(data : {buffer (raw bytes)})
{
        const buffer = data.buffer;
        let vals = new Uint32Array(data.buffer, 0, 8);
        data.now = vals[0] / 1000 + vals[1] * 4294967.296;
        let stride = vals[2];
        data.global_ac_count_withpos = vals[3];
        data.globeIndex = vals[4];

        let limits = new Int16Array(buffer, 20, 4);
        data.south =  limits[0];
        data.west =  limits[1];
        data.north =  limits[2];
        data.east =  limits[3];

        data.messages = vals[7];

        data.aircraft = [];
        for (let off = stride; off < buffer.byteLength; off += stride) {
            let ac = {}
            let u32 = new Uint32Array(buffer, off, stride / 4);
            let s32 = new Int32Array(buffer, off, stride / 4);
            let u16 = new Uint16Array(buffer, off, stride / 2);
            let s16 = new Int16Array(buffer, off, stride / 2);
            let u8 = new Uint8Array(buffer, off, stride);
            let t = s32[0] & (1<<24);
            ac.hex = (s32[0] & ((1<<24) - 1)).toString(16).padStart(6, '0');
            ac.hex = t ? ('~' + ac.hex) : ac.hex;
            ac.seen_pos = u16[2] / 10;
            ac.seen = u16[3] / 10;

            ac.lon = s32[2] / 1e6;
            ac.lat = s32[3] / 1e6;

            ac.baro_rate = s16[8] * 8;
            ac.geom_rate = s16[9] * 8;
            ac.alt_baro = s16[10] * 25;
            ac.alt_geom = s16[11] * 25;

            ac.nav_altitude_mcp = u16[12] * 4;
            ac.nav_altitude_fms = u16[13] * 4;
            ac.nav_qnh = s16[14] / 10;
            ac.nav_heading = s16[15] / 90;

            ac.squawk = u16[16].toString(16).padStart(4, '0');
            ac.gs = s16[17] / 10;
            ac.mach = s16[18] / 1000;
            ac.roll = s16[19] / 100;

            ac.track = s16[20] / 90;
            ac.track_rate = s16[21] / 100;
            ac.mag_heading = s16[22] / 90;
            ac.true_heading = s16[23] / 90;

            ac.wd  = s16[24];
            ac.ws  = s16[25];
            ac.oat = s16[26];
            ac.tat = s16[27];

            ac.tas = u16[28];
            ac.ias = u16[29];
            ac.rc  = u16[30];
            ac.messages = u16[31];

            ac.category = u8[64] ? u8[64].toString(16).toUpperCase() : undefined;
            ac.nic      = u8[65];

            let nav_modes = u8[66];
            ac.nav_modes = true;
            ac.emergency = u8[67] & 15;
            ac.type = (u8[67] & 240) >> 4;

            ac.airground = u8[68] & 15;
            ac.nav_altitude_src = (u8[68] & 240) >> 4;

            ac.sil_type = u8[69] & 15;
            ac.adsb_version = (u8[69] & 240) >> 4;

            ac.adsr_version = u8[70] & 15;
            ac.tisb_version = (u8[70] & 240) >> 4;

            ac.nac_p = u8[71] & 15;
            ac.nac_v = (u8[71] & 240) >> 4;

            ac.sil = u8[72] & 3;
            ac.gva = (u8[72] & 12) >> 2;
            ac.sda = (u8[72] & 48) >> 4;
            ac.nic_a = (u8[72] & 64) >> 6;
            ac.nic_c = (u8[72] & 128) >> 7;


            ac.flight = "";
            for (let i = 78; u8[i] && i < 86; i++) {
                ac.flight += String.fromCharCode(u8[i]);
            }

            ac.dbFlags = u16[43];

            ac.t = "";
            for (let i = 88; u8[i] && i < 92; i++) {
                ac.t += String.fromCharCode(u8[i]);
            }
            ac.r = "";
            for (let i = 92; u8[i] && i < 104; i++) {
                ac.r += String.fromCharCode(u8[i]);
            }
            ac.receiverCount = u8[104];

            ac.rssi = 10 * Math.log(u8[105]*u8[105]/ \
                                    65025 + 1.125e-5)/Math.log(10);

            ac.extraFlags = u8[106];
            ac.nogps = ac.extraFlags & 1;
            if (ac.nogps && nogpsOnly) {
                u8[73] |= 64;
                u8[73] |= 16;
            }

            // must come after the stuff above (validity bits)

            ac.nic_baro      = (u8[73] & 1);
            ac.alert1        = (u8[73] & 2);
            ac.spi           = (u8[73] & 4);
            ac.flight        = (u8[73] & 8)    ? ac.flight       : undefined;
            ac.alt_baro      = (u8[73] & 16)   ? ac.alt_baro     : undefined;
            ac.alt_geom      = (u8[73] & 32)   ? ac.alt_geom     : undefined;

            ac.lat           = (u8[73] & 64)   ? ac.lat          : undefined;
            ac.lon           = (u8[73] & 64)   ? ac.lon          : undefined;
            ac.seen_pos      = (u8[73] & 64)   ? ac.seen_pos     : undefined;

            ac.gs            = (u8[73] & 128)  ? ac.gs           : undefined;

            ac.ias           = (u8[74] & 1)    ? ac.ias          : undefined;
            ac.tas           = (u8[74] & 2)    ? ac.tas          : undefined;
            ac.mach          = (u8[74] & 4)    ? ac.mach         : undefined;
            ac.track         = (u8[74] & 8)    ? ac.track        : undefined;
            ac.calc_track    = !(u8[74] & 8)   ? ac.track        : undefined;
            ac.track_rate    = (u8[74] & 16)   ? ac.track_rate   : undefined;
            ac.roll          = (u8[74] & 32)   ? ac.roll         : undefined;
            ac.mag_heading   = (u8[74] & 64)   ? ac.mag_heading  : undefined;
            ac.true_heading  = (u8[74] & 128)  ? ac.true_heading : undefined;

            ac.baro_rate     = (u8[75] & 1)    ? ac.baro_rate    : undefined;
            ac.geom_rate     = (u8[75] & 2)    ? ac.geom_rate    : undefined;
            ac.nic_a         = (u8[75] & 4)    ? ac.nic_a        : undefined;
            ac.nic_c         = (u8[75] & 8)    ? ac.nic_c        : undefined;
            ac.nic_baro      = (u8[75] & 16)   ? ac.nic_baro     : undefined;
            ac.nac_p         = (u8[75] & 32)   ? ac.nac_p        : undefined;
            ac.nac_v         = (u8[75] & 64)   ? ac.nac_v        : undefined;
            ac.sil           = (u8[75] & 128)  ? ac.sil          : undefined;

            ac.gva                  = (u8[76] & 1)   ? ac.gva              : undefined;
            ac.sda                  = (u8[76] & 2)   ? ac.sda              : undefined;
            ac.squawk               = (u8[76] & 4)   ? ac.squawk           : undefined;
            ac.emergency            = (u8[76] & 8)   ? ac.emergency        : undefined;
            ac.spi                  = (u8[76] & 16)  ? ac.spi              : undefined;
            ac.nav_qnh              = (u8[76] & 32)  ? ac.nav_qnh          : undefined;
            ac.nav_altitude_mcp     = (u8[76] & 64)  ? ac.nav_altitude_mcp : undefined;
            ac.nav_altitude_fms     = (u8[76] & 128) ? ac.nav_altitude_fms : undefined;

            ac.nav_altitude_src     = (u8[77] & 1)   ? ac.nav_altitude_src : undefined;
            ac.nav_heading          = (u8[77] & 2)   ? ac.nav_heading      : undefined;
            ac.nav_modes            = (u8[77] & 4)   ? ac.nav_modes        : undefined;
            ac.alert1               = (u8[77] & 8)   ? ac.alert1           : undefined;
            ac.ws                   = (u8[77] & 16)  ? ac.ws               : undefined;
            ac.wd                   = (u8[77] & 16)  ? ac.wd               : undefined;
            ac.oat                  = (u8[77] & 32)  ? ac.oat              : undefined;
            ac.tat                  = (u8[77] & 32)  ? ac.tat              : undefined;

            if (ac.airground == 1)
                ac.alt_baro = "ground";

            if (ac.nav_modes) {
                ac.nav_modes = [];
                if (nav_modes & 1) ac.nav_modes.push('autopilot');
                if (nav_modes & 2) ac.nav_modes.push('vnav');
                if (nav_modes & 4) ac.nav_modes.push('alt_hold');
                if (nav_modes & 8) ac.nav_modes.push('approach');
                if (nav_modes & 16) ac.nav_modes.push('lnav');
                if (nav_modes & 32) ac.nav_modes.push('tcas');
            }
            switch (ac.type) {
                case  0: ac.type = 'adsb_icao';        break;
                case  1: ac.type = 'adsb_icao_nt';     break;
                case  2: ac.type = 'adsr_icao';        break;
                case  3: ac.type = 'tisb_icao';        break;
                case  4: ac.type = 'adsc';             break;
                case  5: ac.type = 'mlat';             break;
                case  6: ac.type = 'other';            break;
                case  7: ac.type = 'mode_s';           break;
                case  8: ac.type = 'adsb_other';       break;
                case  9: ac.type = 'adsr_other';       break;
                case 10: ac.type = 'tisb_trackfile';   break;
                case 11: ac.type = 'tisb_other';       break;
                case 12: ac.type = 'mode_ac';          break;
                default: ac.type = 'unknown';
            }
            const type4 = ac.type.slice(0, 4);
            if (type4 == 'adsb') {
                ac.version = ac.adsb_version;
            } else if (type4 == 'adsr') {
                ac.version = ac.adsr_version;
            } else if (type4 == 'tisb') {
                ac.version = ac.tisb_version;
            }
            if (stride == 112) {
                let part2 = u32[27].toString(16).padStart(8, '0');
                ac.rId = part2.slice(0, 4) + '-' + part2.slice(4);
            }

            data.aircraft.push(ac);
        }
    }"""
