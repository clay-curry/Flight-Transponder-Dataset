from multiprocessing import Process, Queue
from typing import List
import sys
from sqlalchemy import create_engine
from ..persistence.aircraft import AircraftWaypoint
from ..persistence.airspace import Airspace

in_memory: List[AircraftWaypoint] = []
memory_limit = 0

class SQLite3(Process):
    def __init__(self, cache_max, waypoints: Queue, start_writing, verbose: bool = True) -> None:
        Process.__init__(self)
        self.engine = create_engine("sqlite://", future=True) 
        self.in_memory: List[AircraftWaypoint] = []
        self.cache_max = cache_max
        self.verbose = verbose
        self.waypoints = waypoints
        self.start_writing = start_writing

    def run(self):
        self.start_writing.acquire()
        while not self.waypoints.empty():
            self.in_memory.extend(self.waypoints.get())
        if sys.getsizeof(self.in_memory) > self.cache_max:
            self.flush_buffer()
        if self.verbose:
            num_bytes = sys.getsizeof(self.in_memory)
            units = 'bytes'
            if num_bytes > 1000:
                num_bytes /= 1000
                units = 'kilobytes'
            if num_bytes > 1000:
                num_bytes /= 1000
                units = 'megabytes'
            if num_bytes > 1000:
                num_bytes /= 1000
                units = 'gigabytes'
            print(f'In Memory: { len(self.in_memory) } waypoints')
            print(f'Used Memory: { str(num_bytes) } {units}')
       

    def flush_buffer(self):
        with self.engine.connect() as e:
            print(f'Flushed {len(self.in_memory)} waypoints')
            self.in_memory: List[AircraftWaypoint]
        