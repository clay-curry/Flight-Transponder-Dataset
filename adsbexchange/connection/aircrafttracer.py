from multiprocessing.connection import Connection
from queue import Full
from re import L
from typing import List, Tuple
from multiprocessing import Process, Queue
from threading import Thread
from math import ceil
import requests as re
from time import time, sleep
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine 
from adsbexchange import connection
from ..persistence.aircraft import Aircraft
from ..persistence.aircraftwaypoint import AircraftWaypoint


DELAY_BETWEEN_REQUESTS      = 1.6       # seconds
MAX_PLANES_EACH_REQUEST     = 8         # number of planes
PING_PLANE_EVERY            = 5 * 60    # delay between planes


class AircraftTracer(Thread):
    """AircraftTracer is an I/O bound process for executing massive network requests with server. (Recall, a program is I/O bound if it would go faster if the I/O subsystem was faster). 

    AircraftTracer maintains a list of known Aircraft, together with related attributes

    Author:
        Clay Curry
    """
    # IO Bound Process

    def __init__(self, index: int, parent_conn: Connection, child_conn: Connection, decode_queue: Queue):
        Thread.__init__(self)
        # Interprocess communication
        self.index                      = index
        self.conn                       = parent_conn
        self._conn_to_parent            = child_conn
        self.decode_queue               = decode_queue
        
        # Administering network requests
        self.last_request               = 0
        self.session: re.Session        = None
        self._db_reader: Engine         = None
        self.aircrafts: List[Aircraft]   = []
        self.errors: int                = 0
        
        
    def run(self):
        try:
            self.session = connection.new_session()
            self._db_reader = create_engine(f"sqlite:///{connection.NAME_DB}", echo=connection.ECHO_DB, future=True)
            self._conn_to_parent.send("SUCCESS")
        except Exception as e:
            self._conn_to_parent.send("ERROR")

        while True:
            try:
                timeout = None if len(self.aircrafts) == 0 else 0
                if self._conn_to_parent.poll(timeout):
                    m = self._conn_to_parent.recv()
                    if m == "ADD":
                        add_aircraft(self)
                    elif m == "REMOVE":
                        remove_aircraft(self)
                else:
                    trace_aircrafts(self)
            except Exception as e:
                self._conn_to_parent.send("ERROR")             

def trace_aircrafts(self):
    requests = execute_requests(self)
    ac_list, waypoint_list = decode(self, requests)

def add_aircraft(self: AircraftTracer):
    ac: Aircraft
    while True:
        ac = self._conn_to_parent.recv()
        if ac == "DONE":
            break
        else:
            if ac in self.aircrafts:
                return
            
            with self._db_reader.connect() as conn:
                resp = conn.execute(
                    text(f'SELECT last_track_fetch FROM {connection.AIRCRAFTS_TABLE} WHERE hex="{ac.hex}"')
                )
                if len(resp) > 0:
                    ac.last_track_fetch = resp["last_track_fetch"]
            self.aircrafts.append(ac)
        
def remove_aircraft(self):
    while True:
        ac = self._conn_to_parent.recv()
        if ac == "DONE":
            break
        elif ac in self.aircrafts:
            self.aircrafts.remove(ac)

def execute_requests(self) -> List[Tuple[re.Response, re.Response]]:
    batch_size = min(MAX_PLANES_EACH_REQUEST, len(self.aircrafts))
    n_batches = ceil(len(self.aircrafts) / batch_size)
    requests = []
    
    for b in range(n_batches):
            
        batch = self.aircrafts[b*batch_size:(b+1)*batch_size]
        while (self.last_request + DELAY_BETWEEN_REQUESTS) > time():
            sleep(0.2)
        self.last_request = time()
        
        threads = []
        for aircraft in batch:
            t = RequestThread(self.session, aircraft.hex)
            t.start()
            threads.append(t)

        for t in threads:
            recent, full, hex = t.join()
            while full.status_code != 200:
                errors += 1
                self.session = connection.new_session()
                t = RequestThread(self.session, hex)
                t.start()
                recent, full, hex = t.join()
            
            requests.append((recent, full))

        print(f'Tracer ({self.index}) gathered a batch ({b} / {n_batches}) of its assigned historical tracks. Errors Ecountered: {self.errors}')

    return requests

class RequestThread(Thread):
    def __init__(self, session: re.Session, hexidec: str):
        Thread.__init__(self)
        self.session = session
        self.hexidec = hexidec.lower()
        self._return = None

    def run(self):
        data_prefix = '/data/traces/' # last two of icao hex
        data_recent_midfix = '/trace_recent_'
        data_full_midfix = '/trace_full_'  # icao hex
        data_suffix = '.json'
        last_two = self.hexidec[-2:]
        url = connection.server_URL + data_prefix + last_two + data_recent_midfix + self.hexidec + data_suffix
        recent = self.session.get(url=url)
        url = connection.server_URL + data_prefix + last_two + data_full_midfix + self.hexidec + data_suffix 
        full = self.session.get(url=url)
        self._return = recent, full, self.hexidec

    def join(self):
        Thread.join(self)
        return self._return


    