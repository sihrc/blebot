import traceback

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils import database_exists, create_database

DATABASE = {
    'drivername': 'postgresql',
    'host': 'localhost',
    'port': '5432',
    'username': 'blebot',
    'password': 'blerocks',
}

Base = declarative_base()

def connection(db_name):
    config = dict(DATABASE)
    config["database"] = db_name
    return create_engine(URL(**config))

def get_session(db_name):
    conn = connection(db_name)
    return sessionmaker(bind=conn)()

def create_database(db_name):
    config = dict(DATABASE)
    config["database"] = "template1"
    url = URL(**config)
    engine = create_engine(url)
    if not engine.execute("SELECT 1 FROM pg_database WHERE datname=\'{0}\'".format(db_name)).scalar():
        engine.raw_connection().set_isolation_level(0)
        engine.execute("CREATE DATABASE \"{0}\"".format(db_name))

    conn = connection(db_name)
    Base.metadata.create_all(bind=conn)
