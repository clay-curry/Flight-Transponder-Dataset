from typing import List
import sys
from sqlalchemy import create_engine
from ..persistence.aircraft import AircraftWaypoint

in_memory: List[AircraftWaypoint] = []
memory_limit = 0

# CPU Bound Process
class SQLite3:
    def __init__(self) -> None:
        self.in_memory: List[AircraftWaypoint] = []
        self.add_buffer([])

    def add_buffer(self, crafts: List[AircraftWaypoint]) -> None:
        self.in_memory.extend(crafts)
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
