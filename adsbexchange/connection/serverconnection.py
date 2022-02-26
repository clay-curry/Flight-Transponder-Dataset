import requests as re
from logging import basicConfig, getLogger, debug, info, DEBUG, CRITICAL
from ..datum.airspace import Airspace

# suppresses warnings during server request
getLogger("requests").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)


server_URL = 'https://globe.adsbexchange.com'
# current time (ms, since 1970)
header_conf = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "if-none-match": "\"620589bd-21b8\"",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"98\", \"Google Chrome\";v=\"98\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://globe.adsbexchange.com/?disable_fi=1",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

class ServerConnection:
    """Establishes a connection with adsbexchange.com, a crowd-source depository of real-time ADS-B signals
    being actively broadcasted around the globe.
    """
    def __init__(self):
        self.sess = self.new_session()
        self.index_html = self.sess.get(server_URL)
        info(f'{server_URL} returned with status {self.index_html.status_code}')
        if self.index_html.status_code >= 400:
            raise re.ConnectionError(
                f"ServerConnection object could not connect to {server_URL}")
            return
        info(f'connection with server established. creating threads')
        self.airspace_listener = AirspaceListener(self)
          

    def add_airspace(self, airspace: Airspace):
        self.airspace_listener.add_airspace(airspace)
            

    def remove_airspace(self, airspace: Airspace):
        pass
    
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


from .airspacelistener import AirspaceListener
from .serverclient import ServerClient


if __name__ == "__main__":
    import time
    basicConfig(format="%(message)s", level=DEBUG)

    tic = time.perf_counter()
    conn = ServerConnection()
    toc = time.perf_counter()
    print(f"created Connection object in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    r = conn.fetch_tile("5988")
    toc = time.perf_counter()
    print(f"fetched tile in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    acl = conn.decode_response(r)
    toc = time.perf_counter()
    print(f"decoded response in {toc - tic:0.4f} seconds")

    print(f'NUMBER PLANES = {len(acl)}')
    print(f'string example: {acl[0].to_list()}')
    print(f'dict example: {acl[0].to_dict()}')
    print(f'response = {[(ac.hex, ac.lat, ac.lon, len(ac)) for ac in acl]}')
