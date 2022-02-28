from typing import List, Dict
from multiprocessing import Process, Queue
import queue
from threading import Thread
from requests.models import Response
import requests as re
import regex as rx
from time import time, sleep
from ..persistence.airspace import Airspace
from adsbexchange import connection
from math import ceil

server_URL = connection.server_URL
header_conf = connection.header_conf


max_simultaneous_requests = 8
seconds_between_requests = .5  # seconds


class AirspaceListener(Process):
    """ServerClient is an I/O bound process for executing massive network requests with server. (Recall, a program is I/O bound if it would go faster if the I/O subsystem was faster). 

    Only two of these processes should exist. The first process is for GlobalTile requests. The second process is for individual historical flight track requests. These two processes are designed to strictly follow proper network protocols with the server so that data transfer is maximized and connections are not rejected.

    If an issue arises with the Server, this process is terminated by the parent process.

    Args:
        sess: re.Session: _description_

    Returns:
        _type_: _description_

    Author:
        Clay Curry
    """
    # IO Bound Process

    def __init__(self, session: re.Session, main_queue: Queue, decode_queue: Queue):
        Process.__init__(self)
        self.tracked_airspaces: List[Airspace]  = []
        self.tracked_tiles: Dict[int, int] = {}
        self.last_request               = 0
        self.session                    = session
        self.main_queue                 = main_queue
        self.decode_queue               = decode_queue
        self.max_simultaneous = 8
        
    def run(self):
        index = 0
        self.request_queue              = queue.Queue()   
        
        while True:
            try:
                m = None
                m = self.main_queue.get(block=(len(self.tracked_tiles) == 0))
                if m == "ADD":
                    self.add_airspaces()
                elif m == "DELETE":
                    self.delete_airspaces()
                elif m == 'KILL':
                    self.kill_myself()
            except queue.Empty:
                self.update_tiles()
               
                    

    def update_tiles(self):
        errors = []
        class RequestThread(Thread):
            def __init__(self, session: re.Session, tile_index: int):
                Thread.__init__(self)
                self.session = session
                self.tile_index = tile_index
                self._return = None
            def run(self):
                data_prefix = '/data/globe_'
                data_suffix = '.binCraft'
                url = server_URL + data_prefix + str(self.tile_index).zfill(4) + data_suffix
                self._return = self.session.get(url=url)         
            def join(self):
                Thread.join(self)
                return self._return
        
        tiles = list(self.tracked_tiles.keys())
        batch_size = self.max_simultaneous
        n_batches = ceil(len(tiles) / batch_size)
        requests = []
        for i in range(n_batches):
            print(f'scanning batch {i}/{n_batches}')
            batch = tiles[i*batch_size:(i+1)*batch_size]
            while (self.last_request + seconds_between_requests) > time():
                sleep(0.2)
            self.last_request = time()
            threads = []
            for tile in batch:
                t = RequestThread(self.session, tile)
                t.start()
                threads.append(t)
            for t in threads:
                r = t.join()
                if r.status_code != 200:
                    url = r.url
                    index = rx.findall(r'\d+', url)[0]
                    print(f"airspace {index} returned with an error")
                    self.tracked_tiles.pop(int(index))
                    errors.append(int(index))
                else:    
                    requests.append(r)
            
        self.decode_queue.put(requests)
        
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

    def kill_myself(self):
        self.decode_queue.put('KILL')
        self.kill()

