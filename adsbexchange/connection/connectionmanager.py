from inspect import trace
from multiprocessing import Queue, Pipe
from multiprocessing.connection import Connection
from typing import List, Dict, Tuple
from ..persistence.airspace import Airspace
from ..persistence.aircraft import Aircraft

from .airspacelistener import AirspaceListener
from .aircrafttracer import AircraftTracer
from .airspacedecoder import AirspaceDecoder
from .decoder import Decoder
from .dbwriter import DBWriter


MAX_AIRSPACE_LISTENERS  = 5
PREF_TILES_PER_LISTENER = 64
MAX_TILES_PER_LISTENER  = 120

EXPECTED_AIRCRAFTS = 60000  # aircrafts
FULL_SWEEP_EVERY = 60       # min
AIRCRAFT_PER_REQUEST = 4    # aircrafts
DELAY_BETWEEN_REQUESTS = 1.6 # sec
NUMBER_AIRCRAFT_TRACERS = EXPECTED_AIRCRAFTS * DELAY_BETWEEN_REQUESTS / (FULL_SWEEP_EVERY * AIRCRAFT_PER_REQUEST * 60)



class ConnectionManager:
    """Establishes and manages multiple connections with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """
    def __init__(self):
        # For managing recording states
        self.tracked_airspaces : List[Airspace]          = {} # Airspace Object: List[Tile Indices]
        self.tracked_tiles: Dict[int, Tuple(int, AirspaceListener)] = {} # Tile Index: (Multiplicity, Listener)
        self.tracked_aircrafts: Dict[Aircraft, AircraftTracer]           = {} # hexidecimal identifiers of known aircrafts

        # Message passing for interprocess communication
        self.writer   = DBWriter(database_queue=Queue())
        self.decoder  = Decoder(decode_queue=Queue(), database_queue=self.writer.db_queue)
        self.writer.start()
        self.decoder.start()
        self.listeners: List[AirspaceListener]         = _initialize_listeners(self, MAX_AIRSPACE_LISTENERS)
        self.tracers: List[AircraftTracer]             = _initialize_tracers(self, NUMBER_AIRCRAFT_TRACERS)


    def add_airspace(self, airspace: Airspace) -> None:
        "accepts an Airspace and assigns it to one or several AirspaceListeners"
        if airspace in self.tracked_airspaces:
            return

        # No duplicate assignments
        tiles = airspace.tiles.copy()
        for t in tiles:
            if t in self.tracked_tiles:
                tiles.remove(t)

        while len(tiles) > 0:
            listener, capacity = get_available_listener(self)
            listener.tiles = tiles[0:capacity]
            listener.conn.send('ADD')
            [listener.conn.send(tile) for tile in tiles[0:capacity]]
            listener.conn.send('DONE')
            self.tracked_tiles.update({tile: (0, listener) for tile in tiles[0:capacity]})
            tiles = tiles[capacity:]


        for tile in airspace.tiles:
            (v, l) = self.tracked_tiles[tile]
            self.tracked_tiles[tile] = (v+1, l)

        
    def remove_airspace(self, airspace: Airspace) -> Airspace:
        if airspace not in self.airspaces:
            return
        else:
            delete_dict: Dict[AirspaceListener, List[int]] = {}
            for t in airspace.tiles:
                multiplicity, listener = self.tracked_tiles[t]
                if multiplicity == 1:
                    del self.tracked_tiles[t]
                    listener.tiles.remove(t)
                    delete_dict.setdefault(listener, []).append(t)
                else:    
                    self.tracked_tiles[t][0] -= 1

            for k, v in delete_dict.items():
                k.conn.send('DELETE')
                [k.conn.send(tile) for tile in v]
                k.conn.send('DONE')            


    def list_airspaces(self) -> List[Airspace]:
        return self.tracked_airspaces.copy()


    def add_aircraft(self, aircraft: Aircraft) -> None:
        if aircraft in self.tracked_aircrafts.keys():
            return

        tracer = get_available_tracer(self)
        self.tracked_aircrafts[aircraft] = tracer
        tracer.aircrafts.append(aircraft)
        tracer.conn.send('ADD')
        tracer.conn.send(aircraft)
        tracer.conn.send('DONE')


    def remove_aircraft(self, aircraft: Aircraft) -> Aircraft:
        if aircraft not in self.tracked_aircrafts.keys():
            return

        tracer = self.tracked_aircrafts.pop(aircraft)
        tracer.aircrafts.remove(aircraft)
        tracer.conn.send('DELETE')
        tracer.conn.send(aircraft)
        tracer.conn.send('DONE')
        

    def list_aircraft(self) -> List[Aircraft]:
        return self.tracked_aircrafts.copy()
    

    def kill_children(self):
        [listener.kill() for listener in self.listeners]
        [tracer.kill() for tracer in self.tracers]
        if self.decoder is not None:
            self.decoder.kill()
        if self.writer is not None:
            self.writer.kill()


    def __del__(self):
        print("Called Destructor on ConnectionManager")
        self.kill_children()


def _initialize_listeners(self, num) -> List[AirspaceListener]:
    threads: List[AirspaceListener] = []
    for i in range(num):
        parent_conn, child_conn = Pipe()
        t = AirspaceListener(index=i, parent_conn=parent_conn, child_conn=child_conn, decode_queue=self.decoder.decode_queue)
        t.start()
        threads.append(t)
    return threads

def _initialize_tracers(self, num) -> List[AircraftTracer]:
    threads: List[AircraftTracer] = []
    for i in range(int(num)):
        parent_conn, child_conn = Pipe()
        t = AircraftTracer(index=i, parent_conn=parent_conn, child_conn=child_conn, decode_queue=self.decoder.decode_queue)
        t.start()
        threads.append(t)
    return threads



def get_available_listener(self) -> Tuple[AirspaceListener, int]:
        """returns a tuple containing a Connection to the next available AirspaceListener with its capacity"""
        # 1. Get the next listener below preferred capacity
        for listener in self.listeners:
            size = len(listener.tiles)
            if size < PREF_TILES_PER_LISTENER:
                return listener, PREF_TILES_PER_LISTENER - size

        # 2. Make a new listener if above preferred capacity
        if len(self.listeners) < MAX_AIRSPACE_LISTENERS:
            index = 0
            if len(self.listeners) > 0:    
                index = max([l.index for l in self.listeners]) + 1
            parent_conn, child_conn = Pipe()
            listener = AirspaceListener(index=index, parent_conn=parent_conn, child_conn=child_conn, decode_queue=self.decoder.decode_queue)
            listener.start()
            if parent_conn.recv() != 'SUCCESS':
                raise ConnectionRefusedError("An AirspaceListener could not connect to the server")
            self.listeners.append(listener)            
            return listener, PREF_TILES_PER_LISTENER

        # 3. Get all  
        for listener in self.listeners:
            size = len(listener.tiles)
            capacity = MAX_TILES_PER_LISTENER - size
            if capacity > 0:
                return listener, capacity
        
        raise ConnectionError("The request for additional listeners exceeds available capacity.")
        
def assign_tracer(self: ConnectionManager) -> AircraftTracer:
    # 1. Get the next listener below preferred capacity
        for tracer in self.tracers:
            size = len(tracer.aircrafts)
            if size < PREF:
                return tracer

        # 2. Make a new listener if above preferred capacity
        if len(self.tracers) < NUMBER_TRACERS:
            index = 0
            if len(self.tracers) > 0:    
                index = max([l.index for l in self.listeners]) + 1
            parent_conn, child_conn = Pipe()
            tracer = AircraftTracer(index=index, parent_conn=parent_conn, child_conn=child_conn, waypoint_queue=self.writer.database_queue)
            tracer.start()
            if parent_conn.recv() != 'SUCCESS':
                raise ConnectionRefusedError("An AirspaceListener could not connect to the server")
            self.tracers.append(tracer)            
            return tracer

        # 3. Get any available spot  
        for tracer in self.tracers:
            size = len(tracer.aircrafts)
            capacity = MAX_TILES_PER_LISTENER - size
            if capacity > 0:
                return tracer
        
        raise ConnectionError("The request for additional Tracers exceeds available capacity.")


# IGNORE THIS: suppresses warnings during server request
from logging import getLogger, CRITICAL
getLogger("requests").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)
