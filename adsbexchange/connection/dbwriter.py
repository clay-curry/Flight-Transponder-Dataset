from email import message
from multiprocessing import Process, Queue, connection
import sqlite3
from typing import List
import sys
from urllib import request

from ..persistence.aircraftwaypoint import AircraftWaypoint
from ..persistence.aircraft import Aircraft

from sqlalchemy import create_engine
from sqlalchemy import text
from adsbexchange import connection


# CPU Bound Process
class DBWriter(Process):
    def __init__(self, database_queue: Queue):
        Process.__init__(self)
        self.db_queue = database_queue
        self.engine = None
        self.waypoint_count = 0
        self.aircraft_count = 0
        

    def run(self):
        self.engine = create_engine(f'sqlite:///{connection.NAME_DB}', echo=connection.ECHO_DB, future=True)
        with self.engine.connect() as conn:
            conn.execute(
                text(connection.WAYPOINTS_CREATE_TABLE)
                )
            conn.execute(
                text(connection.AIRCRAFTS_CREATE_TABLE)
            )
            conn.commit()

        while True:
            message = self.db_queue.get(block=True)
            if message == "WAYPOINTS":
                self.insert(connection.WAYPOINTS_INSERT)
            if message == "AIRCRAFTS":
                self.insert(connection.AIRCRAFTS_INSERT)
                
    def insert(self, insert_msg):
        wpts = []
        hex = []
        msg = ""
        while msg != "DONE":
            msg = self.db_queue.get(block=True)            
            if type(msg) == list:
                wpts.extend(msg)
                hex.extend([h.hex for h in msg])
            else:
                wpts.append(msg)
                hex.append(msg.hex)

        with self.engine.connect() as sess:
            try:
                for wp in wpts:
                    sess.execute(
                        text(insert_msg),
                            [wp.to_dict()]
                        )
                    self.waypoint_count += 1


            except Exception as e:
                if connection.ECHO_DB:
                    print(f'due to an error ({e}), the following waypoint was not added: {ac}')
            finally:
                sess.commit()
                print(f"The application has written {wp} live waypoints.")