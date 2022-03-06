from multiprocessing import Process, Queue
import sqlite3
from typing import List
import sys

from ..persistence.aircraftwaypoint import AircraftWaypoint

STACK_MAX = 0   # bytes 

from sqlalchemy import MetaData, create_engine
from sqlalchemy import text

NAME_DB = "adsbexchange/connection/adsbexchange.db"
ECHO_DB = False
WAYPOINTS_TABLE = 'waypoints'
WAYPOINTS_CREATE_TABLE = f'''
CREATE TABLE IF NOT EXISTS {WAYPOINTS_TABLE} (
    row_id                      INTEGER         PRIMARY KEY    AUTOINCREMENT,
    hex                         TEXT            NOT NULL,
    seen_pos                    REAL            NOT NULL,
    seen                        REAL            NOT NULL,
    lat                         REAL            NOT NULL,
    lon                         REAL            NOT NULL,
    baro_rate                   TEXT,
    geom_rate                   TEXT,
    alt_baro                    INTEGER            NOT NULL,
    alt_geom                    INTEGER            NOT NULL,
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
WAYPOINTS_COLUMN = "(hex, seen_pos, seen, lat, lon, baro_rate, geom_rate, alt_baro, alt_geom, nav_altitude_mcp, nav_altitude_fms, nav_qnh, nav_heading, squawk, gs, mach, roll, track, track_rate, mag_heading, true_heading, wd, ws, oat, tat, tas, ias, rc, messages, category, nic, nav_modes, emergency, type, airground, nav_altitude_src, sil_type, adsb_version, adsr_version, tisb_version, nac_p, nac_v, sil, gva, sda, nic_a, nic_c, flight, dbFlags, t, r, receiverCount, rssi, extraFlags, nogps, nic_baro, alert1, spi, calc_track, version, rId)"


# CPU Bound Process
class WaypointWriter(Process):
    def __init__(self, database_queue: Queue):
        Process.__init__(self)
        self.database_queue = database_queue

    def run(self):
        in_memory: List[AircraftWaypoint] = []
        engine = create_engine(f'sqlite:///{NAME_DB}', echo=ECHO_DB, future=True)
        meta = MetaData()
        meta.reflect(engine)
        waypoint_count = 0
        with engine.connect() as sess:
            if f'{WAYPOINTS_TABLE}' not in meta.tables.values():
                sess.execute(
                    text(WAYPOINTS_CREATE_TABLE)
                )
            
            while True:
                waypoints = self.database_queue.get(block=True)
                in_memory.extend(waypoints)
                
                print(f"Pushed {waypoint_count} waypoints since start of program")
                if ECHO_DB:
                    log_memory(in_memory)

                if sys.getsizeof(in_memory) > STACK_MAX:
                    for ac in in_memory:
                        try:
                            sess.execute(
                                text(WAYPOINTS_INSERT),
                                [ac.to_dict()]
                            )
                            waypoint_count += 1
                        except Exception as e:
                            if ECHO_DB:
                                print(f'due to an error ({e}), the following waypoint was not added: {ac}')
                    sess.commit()
                    in_memory = []


def log_memory(in_memory):
    space = sys.getsizeof(in_memory)
    units = 'bytes'
    if space > 1000:
        space /= 1000
        units = 'kilobytes'
    if space > 1000:
        space /= 1000
        units = 'megabytes'
    if space > 1000:
        space /= 1000
        units = 'gigabytes'
    print(f'In Memory: { len(in_memory) } waypoints')
    print(f'Used Memory: { str(space) } {units}')