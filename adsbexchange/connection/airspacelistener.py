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

SKIP_CONN = False

class AirspaceListener(Process):
    """
    AirspaceListener is an I/O bound process for executing massive network requests with server. 
    (Recall, a program is I/O bound if it would go faster if the I/O subsystem was faster). 

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
        Process.__init__(self)
        # Interprocess communication
        self.index              = index
        self.conn               = parent_conn
        self._child_conn       = child_conn
        self._decode_queue      = decode_queue
        
        # Administering network requests
        self.last_request         = 0
        self.session: re.Session  = None
        self.tiles                = []
        
        
    def run(self):
        try:
            if SKIP_CONN:
                pass
            else:
                self.session = self.new_session()
                r = self.session.get(server_URL)
                if r.status_code != 200:
                    print("An airspace listener failed to form a connection with server. Trying again in 2 seconds")
                    sleep(2)
                    self.session = self.new_session()
                    r = self.session.get(server_URL)
                    if r.status_code != 200:
                        self._child_conn.send("ERROR")
        except:
            self._child_conn.send("ERROR")
        
        self._child_conn.send('SUCCESS')

        while True:
            try:
                timeout = None if len(self.tiles) == 0 else 0
                if self._child_conn.poll(timeout):
                    m = self._child_conn.recv()
                    if m == "ADD":
                        self.append_tiles()
                    elif m == "REMOVE":
                        self.remove_tiles()
                    elif m == "LIST":
                        self._child_conn.send(self.tiles.copy())
                    elif m == "RECONNECT":
                        self.session = self.new_session()
                    
                else:
                    self.update_tiles()
            except:
                self._child_conn.send("ERROR")             

    def update_tiles(self):
        batch_size = min(MAX_TILES_EACH_REQUEST, len(self.tiles))
        
        n_batches = ceil(len(self.tiles) / batch_size)
        requests = []

        errors = 0
        for b in range(n_batches):
            print(f'Listener ({self.index}) scanning batch {b+1}/{n_batches}. Errors Ecountered: {errors}')
            
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
                    print(f"airspace {index} returned with an error. Attempting to restore connection")    
                    self.session = self.new_session()
                    t = RequestThread(self.session, index)
                    t.start()
                    r, index = t.join()
                    sleep(5)
                else:    
                    retry = False
                    requests.append(r)
            
        self._decode_queue.put(requests)

    def new_session(self) -> re.Session:
        from time import time
        from random import choices
        from string import ascii_lowercase
        from urllib3.exceptions import HeaderParsingError
        
        
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
        except HeaderParsingError:
            # the server's responses cause urllib to throw a HeaderParsingError 
            # (this is normal and a result of their data compression scheme)
            pass
            
        s = re.Session()
        s.headers = header_conf
        s.headers['cookie'] = cookie
        return s

    def append_tiles(self):
        while True:
            tile = self._child_conn.recv()
            if tile == "DONE":
                break
            else:
                self.tiles.append(tile)
            
    def remove_tiles(self):
        while True:
            tile = self._child_conn.recv()
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
