from socket import timeout
from typing import List
from multiprocessing import Process, Semaphore, Queue
from threading import Thread, Timer
from requests.models import Response
import requests as re
from time import time, sleep

from . import serverconnection
from ..persistence.airspace import Airspace
from adsbexchange import connection
server_URL = connection.server_URL
header_conf = connection.header_conf


max_simultaneous_requests = 8
elapse_between_requests = 1.8  # seconds


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

    def __init__(self, session: re.Session, requests: Queue, start_recording,start_decoding,add_airspace_queue,remove_airspace_queue):
        Process.__init__(self)
        self.airspaces: List[Airspace] = []
        self.last_request = time()  # avoid HTTP 429 error
        self.session = session           # cookies and other headers
        self.requests = requests
        self.start_recording = start_recording
        self.start_decoding = start_decoding
        self.start_decoding.acquire() # avoid racing condition with decoder
        self.add_airspace_queue = add_airspace_queue
        self.remove_airspace_queue = remove_airspace_queue
        
    def run(self):
        index = 0
        while True:
            try:
                self.start_recording.acquire()
                self.start_recording.release()
                while not self.remove_airspace_queue.empty():
                    i = self.airspaces.index(self.remove_airspace_queue.get())
                    self.airspaces.pop(i)
                while not self.add_airspace_queue.empty():
                    self.airspaces.append(self.add_airspace_queue.get())
                request_queue = self.airspaces[index].tiles
                index += 1
                index %= len(self.airspaces)
                # avoid Too Many Requests (HTTP 429) error
                while (self.last_request + elapse_between_requests) > time():
                    sleep(0.2)
                self.last_request = time()

                #t = Timer(20)    # server timeout
                threads = []
                for r in request_queue:
                    crawler = Thread(target=self.request, args=(r[0],))
                    crawler.start()
                    threads.append(crawler)
                for crawler in threads:
                    crawler.join()
                self.start_decoding.release() # "start decoding" semaphore
                #t.cancel()
            
            except:
                pass

    def request(self, path) -> Response:
        data_prefix = '/data/globe_'
        data_suffix = '.binCraft'
        url = server_URL + data_prefix + str(path) + data_suffix
        r = self.session.get(url=url)
        self.requests.put(r)
        return r