from socket import timeout
from typing import List
from multiprocessing import Process, Queue, Semaphore

from threading import Thread, Timer
from requests.models import Response
import requests as re
from time import time, sleep
from . import serverconnection

server_URL = serverconnection.server_URL
header_conf = serverconnection.header_conf

max_simultaneous_requests = 8
elapse_between_requests = 1.8  # seconds


class ServerClient(Process):
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

    def __init__(self, sess: re.Session, paths: Queue, requests: Queue):
        Process.__init__(self, group=None)
        self.sess = sess           # cookies and other headers
        self.paths = paths   # contains paths
        self.requests = requests
        self.last_request = time()  # avoid HTTP 429 error
        self.request_queue = []

    def run(self):
        while True:
            try:
                while (self.paths.empty()):
                    sleep(.1)

                while (not self.paths.empty()):
                    self.request_queue.append(self.paths.get())

                # avoid Too Many Requests (HTTP 429) error
                while (self.last_request + elapse_between_requests) > time():
                    sleep(0.2)
                self.last_request = time()

                requests = []
                max = max_simultaneous_requests
                t = Timer(5, self.kill_myself)    # server timeout
                while len(self.request_queue) > 0 and len(requests) <= max:
                    requests.append(self.request_queue.pop(0))

                threads = []
                for r in requests:
                    crawler = Thread(target=self.request, args=(r,))
                    crawler.start()
                    threads.append(crawler)

                for crawler in threads:
                    crawler.join()

                t.cancel()
            except:
                pass

    def request(self, path) -> Response:
        r = self.sess.get(url=server_URL + path)
        self.requests.put(r)
        return r

    def kill_myself(self):
        # the server stopped responding to me so my life is meaningless
        self.kill()
