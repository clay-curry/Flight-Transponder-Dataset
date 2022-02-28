from multiprocessing import Process, Queue
from typing import List
import sys
from ..persistence.aircraft import AircraftWaypoint


DB_NAME = "waypoints"
DB_ECHO = True


from sqlalchemy import create_engine
from sqlalchemy import text


# CPU Bound Process
class SQLite3(Process):
    def __init__(self, database_queue: Queue):
        Process.__init__(self)
        self.database_queue = database_queue

    def run(self):
        self.in_memory: List[AircraftWaypoint] = []
        self.engine = create_engine(f'sqlite:///{DB_NAME}', echo=DB_ECHO, future=True)
        with self.engine.connect() as conn:
            while True:
                waypoints = self.database_queue.get(block=True)
                self.in_memory.extend(waypoints)
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
