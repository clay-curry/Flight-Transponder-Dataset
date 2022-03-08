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
    # "cookie":   cookie,
    "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


NAME_DB = "adsbexchange/connection/adsbexchange.db"
ECHO_DB = False
WAYPOINTS_TABLE = 'waypoints'
WAYPOINTS_CREATE_TABLE = f'''
CREATE TABLE IF NOT EXISTS waypoints (
    row_id                      INTEGER         PRIMARY KEY    AUTOINCREMENT,
    hex                         TEXT            NOT NULL,
    seen_pos                    REAL            NOT NULL,
    seen                        REAL,
    lat                         REAL            NOT NULL,
    lon                         REAL            NOT NULL,
    baro_rate                   TEXT,
    geom_rate                   TEXT,
    alt_baro                    INTEGER,
    alt_geom                    INTEGER,
    nav_altitude_mcp            TEXT,
    nav_altitude_fms            TEXT,
    nav_qnh                     TEXT,
    nav_heading                 TEXT,
    squawk                      TEXT,
    gs                          TEXT,
    mach                        TEXT,
    roll                        TEXT,
    track                       TEXT,
    track_rate                  TEXT,
    mag_heading                 TEXT,
    true_heading                TEXT,
    wd                          TEXT,
    ws                          TEXT,
    oat                         TEXT,
    tat                         TEXT,
    tas                         TEXT,
    ias                         TEXT,
    rc                          TEXT,
    messages                    TEXT,
    category                    TEXT,
    nic                         TEXT,
    nav_modes                   TEXT,
    emergency                   TEXT,
    type                        TEXT,
    airground                   TEXT,
    nav_altitude_src            TEXT,
    sil_type                    TEXT,
    adsb_version                TEXT,
    adsr_version                TEXT,
    tisb_version                TEXT,
    nac_p                       TEXT,
    nac_v                       TEXT,
    sil                         TEXT,
    gva                         TEXT,
    sda                         TEXT,
    nic_a                       TEXT,
    nic_c                       TEXT,
    flight                      TEXT,
    dbFlags                     TEXT,
    t                           TEXT,
    r                           TEXT,
    receiverCount               TEXT,
    rssi                        TEXT,
    extraFlags                  TEXT,
    nogps                       TEXT,
    nic_baro                    TEXT,
    alert1                      TEXT,
    spi                         TEXT,
    calc_track                  TEXT,
    version                     TEXT,
    rId                         TEXT
    );'''

WAYPOINTS_COLUMNS = "(:hex, :seen_pos, :seen, :lat, :lon, :baro_rate, :geom_rate, :alt_baro, :alt_geom, :nav_altitude_mcp, :nav_altitude_fms, :nav_qnh, :nav_heading, :squawk, :gs, :mach, :roll, :track, :track_rate, :mag_heading, :true_heading, :wd, :ws, :oat, :tat, :tas, :ias, :rc, :messages, :category, :nic, :nav_modes, :emergency, :type, :airground, :nav_altitude_src, :sil_type, :adsb_version, :adsr_version, :tisb_version, :nac_p, :nac_v, :sil, :gva, :sda, :nic_a, :nic_c, :flight, :dbFlags, :t, :r, :receiverCount, :rssi, :extraFlags, :nogps, :nic_baro, :alert1, :spi, :calc_track, :version, :rId)"
WAYPOINTS_INSERT = f"INSERT INTO {WAYPOINTS_TABLE} {WAYPOINTS_COLUMNS.replace(':','')} VALUES {WAYPOINTS_COLUMNS}"
WAYPOINTS_SELECT_UNIQUE_HEX = f"SELECT DISTINCT hex FROM {WAYPOINTS_TABLE}"

AIRCRAFTS_TABLE = 'aircrafts'
AIRCRAFTS_CREATE_TABLE = f'''
CREATE TABLE IF NOT EXISTS {AIRCRAFTS_TABLE} (
    hex                         TEXT            NOT NULL        PRIMARY KEY,
    last_track_fetch            INTEGER         NOT NULL,
    registration                TEXT,
    tail_number                 TEXT,
    description                 TEXT,
    owner                       TEXT,
    year                        TEXT,
    UNIQUE(hex)
    );'''


AIRCRAFTS_COLUMNS = "(:hex, :last_track_fetch, :registration, :tail_number, :description, :owner, :year)"
AIRCRAFTS_INSERT = f"REPLACE INTO {AIRCRAFTS_TABLE} {AIRCRAFTS_COLUMNS.replace(':','')} VALUES {AIRCRAFTS_COLUMNS}"
AIRCRAFTS_SELECT_FETCHORDERED = f"SELECT * FROM {AIRCRAFTS_TABLE} ORDER BY last_track_fetch ASC;"



import requests as re
def new_session() -> re.Session:
        from time import time, sleep
        from random import choices
        from string import ascii_lowercase
        from urllib3.exceptions import HeaderParsingError
        
        # Generate Cookie
        sumbit_time_ms = int(time() * 1000)
        cookie_expire = str(sumbit_time_ms + 2*86400*1000)  # two days
        cookie_token = '_' + \
            ''.join(choices(ascii_lowercase + '1234567890', k=11))
        cookie = 'adsbx_sid=' + cookie_expire + cookie_token

        submit_cookie_url = server_URL + \
            '/globeRates.json?_=' + str(sumbit_time_ms)

        new_cookie_head['cookie'] = cookie
        try:
            r = re.get(submit_cookie_url, headers=new_cookie_head)
            while r.status_code != 200:
                sleep(5)
                r = re.get(submit_cookie_url, headers=new_cookie_head)
        except HeaderParsingError:
            # the server's responses cause urllib to throw a HeaderParsingError 
            # (this is normal and a result of their data compression scheme)
            pass
            
        s = re.Session()
        s.headers = header_conf.copy()
        s.headers['cookie'] = cookie
        r = s.get(server_URL)
        return s