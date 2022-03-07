from multiprocessing import Process, Queue
from multiprocessing.connection import Connection

from threading import Thread
from typing import List, Dict
from os import getpid

from requests.models import Response
import requests as re
import regex as rx
from time import time, sleep
from adsbexchange import connection
from math import ceil


server_URL                  = connection.server_URL
new_cookie_head             = connection.new_cookie_head
header_conf                 = connection.header_conf

DELAY_BETWEEN_REQUESTS      = 1.6  # seconds
MAX_TILES_EACH_REQUEST      = 8

ONLINE = True
OFFLINE = False

class AirspaceListener(Thread):
    """
    AirspaceListener is an I/O bound thread for executing massive network requests with server. 
    (I/O bound if it would go faster if the I/O subsystem was faster). 

    Only two of these I/O processes should exist at once the server. 
    This process systematically asks what's in the sky now. 
    The other process is for individual historical flight track requests. 
    These two processes are designed to strictly follow proper network protocols with the server so that data transfer is maximized and connections are not rejected.

    If an issue arises with the Server, this process is terminated by the parent process.

    Author:
        Clay Curry
    """
    # IO Bound Process

    def __init__(self, index: int, parent_conn: Connection, child_conn: Connection, decode_queue: Queue):
        Thread.__init__(self)
        # Interprocess communication
        self.index              = index
        self.conn               = parent_conn
        self._conn_to_parent    = child_conn
        self._decode_queue      = decode_queue
        
        # Administering network requests
        self.last_request         = 0
        self.session: re.Session  = None
        self.tiles                = []
        self.errors               = 0
        
        
    def run(self):
        try:
            self.session = connection.new_session()
            self._conn_to_parent.send("SUCCESS")
        except:
            self._conn_to_parent.send("ERROR")

        while True:
            try:
                timeout = None if len(self.tiles) == 0 else 0
                if self._conn_to_parent.poll(timeout):
                    m = self._conn_to_parent.recv()
                    if m == "ADD":
                        self.add_tiles()
                    elif m == "REMOVE":
                        self.remove_tiles()
                    elif m == "LIST":
                        self._conn_to_parent.send(self.tiles.copy())
                else:
                    self.update_tiles()
            except:
                self._conn_to_parent.send("ERROR")             

    def update_tiles(self):
        batch_size = min(MAX_TILES_EACH_REQUEST, len(self.tiles))
        n_batches = ceil(len(self.tiles) / batch_size)
        requests = []

        for b in range(n_batches):
            
            batch = self.tiles[b*batch_size:(b+1)*batch_size]
            while (self.last_request + DELAY_BETWEEN_REQUESTS) > time():
                sleep(0.2)
            self.last_request = time()
            
            threads = []
            for index in batch:
                t = RequestThread(self.session, index)
                t.start()
                threads.append(t)

            for t in threads:
                r, index = t.join()
                while r.status_code != 200:
                    self.errors += 1
                    self.session = connection.new_session()
                    t = RequestThread(self.session, index)
                    t.start()
                    r, index = t.join()
                    
                else:    
                    requests.append(r)

            print(f'Listener ({self.index}) gathered a batch ({b} / {n_batches}) of live waypoints. Errors Ecountered: {self.errors}')
            
        self._decode_queue.put(requests)

    def add_tiles(self):
        while True:
            tile = self._conn_to_parent.recv()
            if tile == "DONE":
                break
            else:
                self.tiles.append(tile)
            
    def remove_tiles(self):
        while True:
            tile = self._conn_to_parent.recv()
            if tile == "DONE":
                break
            else:
                self.tiles.remove(tile)



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
        r = self.session.get(url=url,)     
        self._return = r    

    def join(self) -> Response:
        Thread.join(self)
        return self._return, self.tile_index
