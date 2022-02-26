import sqlalchemy

"""
Database Metadata
- describes the structure of the database, i.e. tables, columns, constraints, in terms of data structures in Python
- serves as the basis for SQL generation and object relational mapping
- can generate *to* a schema, i.e. turned into DDL that is emitted to the database
- can be generated *from* a schema, i.e. database introspection is performed to generate Python structures that represent exisitng tables, constratins, etc.
- forms the basis dfor dabase migration tools like SQLAlchemy Alembic
"""

from sqlalchemy import MetaData, Numeric, create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Numeric
from sqlalchemy import select

metadata = MetaData() # 'metadata' is a collection object containing dictionaries and other things describing the various schema of tables

"""
user_table = Table(
    "user",
    metadata,
    Column("amount", Numeric(50), primary_key=True),
    Column("fullname", String(255)),   
) # a 'Table' object in sqlalchemy encapsulates the notion of a possible table. it is no where yet


user_fancy = Table(
    "fancy",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), nullable=False),
) # a 'Table' object in sqlalchemy encapsulates the notion of a possible table. it is no where yet

user_table.c.amount
user_table.c.fullname
user_table.c.fullname.type
user_table.primary_key

print(select(user_table))


engine = create_engine("sqlite://") # no path -> creates an 'in-memory' database; sole purpose is for testing
with engine.begin() as conn:
    metadata.create_all(conn)

# or 

engine = create_engine("sqlite://") # no path -> creates an 'in-memory' database; sole purpose is for testing
with engine.begin() as conn:
    user_table.create(conn)
    user_fancy.create(conn)


print(inspector.get_table_names())
print(inspector.get_columns("user"))
print(())
"""

from sqlalchemy import inspect
from sqlalchemy import ForeignKey

metadata = MetaData() # 'metadata' is a collection object containing dictionaries and other things describing the various schema of tables

user_table = Table(
    "user_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50)),
    Column("fullname", String(50)),   
) # a 'Table' object in sqlalchemy encapsulates the notion of a possible table. it is no where yet

user_email = Table(
    "email_address",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String(100), nullable=False)
)

engine = create_engine("sqlite://")
with engine.begin() as conn:
    metadata.create_all(conn)


""" 
ORM (Object Relational Mapping) is the process of associating object oriented classes with database tables
- we refer tot he set of object oreinted classes as a domain model
- Application =><= Database
- Domain Object \in Application
- Table Row \in Database
- Domain Object ==object.save()==> Table Row
- Table Row ==class.load()==> Domain Object
"""

