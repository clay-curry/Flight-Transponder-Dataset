DB_NAME = "some.db"
DB_ECHO = True


from unicodedata import name
from sqlalchemy import create_engine, MetaData, inspect, insert
from sqlalchemy import text, Table, Column, Integer, String
from sqlalchemy.orm import Session, declarative_base

# The start of any SQLAlchemy application is an object called the Engine. This object acts as a 
# central source of connections to a particular database, providing both a factory as well as a 
# holding space called a connection pool for these database connections.

engine = create_engine(f'sqlite://', echo=DB_ECHO, future=True)

# In relational databases, the basic structure that we create and query from is known 
# as a table. In SQLAlchemy, the “table” is represented by some Table() object
# With SQLAlchemy, a Table() ...
#  - may be declared, (meaning we explicitly spell out in source code what the table looks like)
#  - may be reflected, (meaning we generate the object based on what’s already present in a database)
#  - may be created in many ways by blending the two above approaches
# Whether we will declare or reflect our tables, the MetaData() object is a collection for storing tables

m = MetaData()
m.reflect(engine)               # pull existing database


# Tables in a database are printed as follows
with engine.connect() as conn:
    conn.execute(
        text("""CREATE TABLE some_table (
            x INTEGER PRIMARY KEY, 
            y INTEGER
        );"""
        )
    )
    conn.commit()
    conn.execute(text('CREATE TABLE IF NOT EXISTS some_table (x int, y int)'))
    
m.reflect(engine)
for table in m.tables.values(): # view the tables
    print(table.name)
    
# When using the ORM, the process by which we declare Table metadata is usually combined with the 
# process of declaring mapped classes. When using the ORM, the MetaData collection remains
# present, however it itself is contained within an ORM-only object known as the registry. We create 
# a registry by constructing it:

from sqlalchemy.orm import registry
mapper_registry = registry()

# When using the ORM, instead of declaring Table objects directly, we will now declare them indirectly 
# through directives applied to our mapped classes. In the most common approach, each mapped class 
# descends from a common base class known as the declarative base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

# we can see a Table object from a declarative mapped class using the .__table__ attribute:
User.__table__

class AircraftWaypoint:
    def __init__(self):
        self.hex = self.seen_pos = self.seen = None
        self.lon = self.lat = None
        self.baro_rate =self.geom_rate = self.alt_baro = self.alt_geom = None

WAYPOINTS_TABLE = 'waypoints'
WAYPOINTS_CREATE_TABLE = f'''
CREATE TABLE IF NOT EXISTS {WAYPOINTS_TABLE} (
    rowid         INTEGER    PRIMARY KEY    AUTOINCREMENT,
    hex           INTEGER,
    seen_pos      INTEGER,
    seen          INTEGER,
    baro_rate     INTEGER,
    geom_rate     INTEGER,
    alt_baro      INTEGER,
    alt_geom      INTEGER);
    '''
WAYPOINfTS_COLUMNS = '(:hex, :seen_pos, :seen, :baro_rate, :geom_rate, :alt_baro, :alt_geom)'

ac = AircraftWaypoint()
ac.hex = 123
ac.seen_pos = 100
ac.seen = 100
ac.lon = -95
ac.lat = 103
ac.baro_rate = 25
ac.geom_rate = 20
ac.alt_baro = 2200
ac.alt_geom = 2000

print(ac.__dict__)

with Session(engine) as session:
    session.execute(
        text(WAYPOINTS_CREATE_TABLE)
    )
    session.execute(
       text(f"INSERT INTO {WAYPOINTS_TABLE} {WAYPOINTS_COLUMNS.replace(':','')} VALUES {WAYPOINTS_COLUMNS}"),
       [ac.__dict__, ac.__dict__]
    )

    session.commit()

    result = session.execute(
        text(f'SELECT * FROM {WAYPOINTS_TABLE}')
    )
    for row in result:
        print(row)