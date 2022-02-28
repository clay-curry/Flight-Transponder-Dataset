from http import server
import imp
import sqlite3
from wsgiref.simple_server import server_version
import requests as re
from multiprocessing import Semaphore, Queue
from logging import basicConfig, getLogger, debug, info, DEBUG, CRITICAL
from typing import List
from adsbexchange import connection
from ..persistence.airspace import Airspace
from .airspacelistener import AirspaceListener
from .airspacedecoder import AirspaceDecoder
from .sql import SQLite3

# suppresses warnings during server request
getLogger("requests").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)

tracked_airspaces: List[Airspace] = []
cache_max = 1000000
server_URL = connection.server_URL
header_conf = connection.header_conf


class ServerConnection:
    """Establishes a connection with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """
    def __init__(self):
        self.session = self.new_session()
        self.index_html = self.session.get(server_URL)
        info(f'{server_URL} returned with status {self.index_html.status_code}')
        if self.index_html.status_code >= 400:
            raise re.ConnectionError(
                f"ServerConnection object could not connect to {server_URL}")
            return
        info(f'connection with server established. creating threads')
        self.make_airspace_recorder()
    
    def make_airspace_recorder(self):
        self.main_queue = Queue()
        decode_queue    = Queue()
        database_queue  = Queue()
        self.p_listener = AirspaceListener(self.session, self.main_queue, decode_queue)
        self.p_listener.start()
        
        self.p_decoder  = AirspaceDecoder(decode_queue, database_queue)
        self.p_decoder.start()
        
        self.p_database = SQLite3(database_queue)
        self.p_database.start()
        

    def get_children(self):
        return self.p_listener, self.p_decoder, self.p_database
    
    def add_airspace(self, airspace: Airspace):
        if airspace in tracked_airspaces:
            return
        else:
            tracked_airspaces.append(airspace)
            self.main_queue.put('ADD')
            self.main_queue.put(airspace)
            self.main_queue.put('DONE')
            
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
        self.p_listener.kill()
        self.p_decoder.kill()
        self.p_database.kill()
        self.make_airspace_recorder()
        if len(tracked_airspaces) > 0:
            self.main_queue.put('ADD')
            for airspace in tracked_airspaces:
                self.main_queue.put(airspace)
            self.main_queue.put('DONE')
        
        

    def new_session(self) -> re.Session:
        from time import time
        from random import choices
        from string import ascii_lowercase
        from urllib3.exceptions import HeaderParsingError
        
        s = re.Session()
        s.headers = header_conf

        debug("making new cookie")
        sumbit_time_ms = int(time() * 1000)
        cookie_expire = str(sumbit_time_ms + 2*86400*1000)  # two days
        cookie_token = '_' + \
            ''.join(choices(ascii_lowercase + '1234567890', k=11))
        cookie = 'adsbx_sid=' + cookie_expire + cookie_token

        new_cookie_head = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "cookie":   cookie,
            "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        submit_cookie_to = server_URL + \
            '/globeRates.json?_=' + str(sumbit_time_ms)
        try:
            r = re.get(submit_cookie_to, headers=new_cookie_head)
        except HeaderParsingError:
            debug(f'{submit_cookie_to} caused a HeaderParsingError (this is normal)')

        s.headers['cookie'] = cookie
        return s



if __name__ == "__main__":
    import sys
    conn = ServerConnection()