DB_NAME = "some.db"
DB_ECHO = True


from unicodedata import name
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy import text, Table, Column, Integer, String
from sqlalchemy.orm import declarative_base

engine = create_engine(f'sqlite:///{DB_NAME}', echo=DB_ECHO, future=True)

inspector = inspect(engine)
for table_name in inspector.get_table_names():
    print(table_name)

m = MetaData()
m.reflect(engine)
for table in m.tables.values():
    print(table.name)
    for column in table.c:
        print(column.name)

Base = declarative_base()
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE users (x int, y int)"))
    conn.execute(
        text("INSERT INTO users (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}]
    )
    conn.commit()

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6)

with engine.connect() as conn:
    result = conn.execute(stmt)
    for row in result:
       print(f"x: {row.x}  y: {row.y}")

