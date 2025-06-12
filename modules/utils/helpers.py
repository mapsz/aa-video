from config import DatabaseUri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.models._base import Base
import os
import sys
from pprint import pprint

engine = create_engine(DatabaseUri)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def make_dir(filepath):
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def dd(*args):
    for arg in args:
        pprint(arg)
    sys.exit()
