from multiprocessing import Queue, Pipe
from multiprocessing.connection import Connection
from logging import basicConfig, getLogger, debug, info, DEBUG, CRITICAL
from typing import List, Dict, Tuple
from ..persistence.airspace import Airspace
from .airspacelistener import AirspaceListener
from .aircrafttracer import AircraftTracer
from .airspacedecoder import AirspaceDecoder
from .waypointwriter import WaypointWriter
from time import sleep


MAX_AIRSPACE_LISTENERS  = 2
MAX_TILES_PER_LISTENER  = 120
PREF_TILES_PER_LISTENER = 64
MAX_AIRCRAFT_TRACERS    = 2

ONLINE = True
OFFLINE = False


def make_airspace_decoder() -> Queue:
    decode_queue        = Queue()
    database_queue      = Queue()
    p_decoder           = AirspaceDecoder(decode_queue=decode_queue, database_queue=database_queue)
    p_database          = WaypointWriter(database_queue=database_queue)
    p_decoder.start()
    p_database.start()
    return decode_queue 

def spawn_aircraft_tracer(self) -> AircraftTracer:
    return None

def get_available_listener(self) -> Tuple[Airspace, int]:
        """returns a tuple containing a Connection to the next available AirspaceListener with its capacity"""
        # 1. Get the next listener below preferred capacity
        for airspace in self.listeners.keys():
            size = self.listeners[airspace]
            if size < PREF_TILES_PER_LISTENER:
                return airspace, PREF_TILES_PER_LISTENER - size

        # 2. Make a new listener if above preferred capacity
        if len(self.listeners.keys()) < MAX_AIRSPACE_LISTENERS:
            index = 0
            if len(self.listeners) > 0:    
                index = max([l.index for l in self.listeners]) + 1

            parent_conn, child_conn = Pipe()
            airspace = AirspaceListener(index=index, parent_conn=parent_conn, child_conn=child_conn, decode_queue=self.decoder)
            airspace.start()
            status = parent_conn.recv()
            if status != 'SUCCESS':
                raise ConnectionRefusedError("An AirspaceListener could not connect to the server")
            
            self.listeners[airspace] = 0
            return airspace, PREF_TILES_PER_LISTENER

        # 3. Get all  
        for airspace in self.listeners:
            size = self.listeners[airspace]
            capacity = MAX_TILES_PER_LISTENER - size
            if capacity > 0:
                return airspace, capacity
        
        
        raise ConnectionError("The request for additional listeners exceeds available capacity.")
        

def get_available_tracer(self):
    pass

class ConnectionManager:
    """Establishes and manages multiple connections with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """
    def __init__(self):
        # For managing recording states
        self.tracked_airspaces : Dict[Airspace, List[int]]          = {} # Airspace Object: List[Tile Indices]
        self.tracked_tiles: Dict[int, Tuple(int, AirspaceListener)] = {} # Tile Index: (Multiplicity, Listener)
        self.tracked_aircrafts: Dict[str, AircraftTracer]           = {} # hexidecimal identifiers of known aircrafts

        # Message passing for interprocess communication
        self.listeners: Dict[AirspaceListener, int]                      = {} # Listener Object: (Message Passing Queue)
        self.tracers: List[AircraftTracer]       = {} # Tracer Object:   (Message Passing Queue, number tracked Aircrafts)
        self.decoder = make_airspace_decoder()


    def add_airspace(self, airspace: Airspace):
        if airspace in self.tracked_airspaces:
            return

        add_list = [tile for tile in airspace.tiles if tile not in self.tracked_tiles]
        while len(add_list) > 0:
            listener, capacity = get_available_listener(self)
            sleep(2)
            append = add_list[0:capacity]
            
            listener.conn.send('ADD')
            [listener.conn.send(tile) for tile in append]
            listener.conn.send('DONE')
            self.listeners[listener] += len(append)
            add_list = add_list[capacity:]
            
        for tile in airspace.tiles:
            if tile in self.tracked_tiles.keys():
                self.tracked_tiles[tile] += 1
            else:
                add_list.append(tile)

        self.tracked_airspaces[airspace] = airspace.tiles

        
    def remove_airspace(self, airspace: Airspace):
        if airspace not in self.airspaces:
            return
        else:
            self.main_queue.put('DELETE')
            self.main_queue.put(airspace)
            self.main_queue.put('DONE')
            
    
    def list_airspaces(self):
        return self.p_listener.airspaces.copy()

    def kill_airspace_recorders(self):
        
        self.make_airspace_recorder()
        if len(tracked_airspaces) > 0:
            self.main_queue.put('APPEND')
            for airspace in tracked_airspaces:
                self.main_queue.put(airspace)
            self.main_queue.put('DONE')
            
    def add_airspaces(self):
        while True:
            airspace = self.main_queue.get(block=True)
            if type(airspace) is not Airspace: break
            self.tracked_airspaces.append(airspace)
            for tile in airspace.tiles:
                if tile in self.tracked_tiles.keys():
                    self.tracked_tiles[tile] += 1
                else:
                    self.tracked_tiles[tile] = 1
    
    def delete_airspaces(self):
        while True:
            airspace = self.main_queue.get(block=True)
            if type(airspace) is not Airspace: break
            self.tracked_airspaces.pop(self.tracked_airspaces.index(airspace))
            for tile in airspace.tiles:
                self.tracked_tiles[tile] -= 1
                if self.tracked_tiles[tile] == 0:
                    del self.tracked_tiles[tile]                    
        

# IGNORE THIS: suppresses warnings during server request
getLogger("requests").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)




