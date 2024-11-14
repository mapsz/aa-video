from config import DatabaseUri
from sqlalchemy import create_engine
from modules.models._base import Base
from modules import Reddit
from modules import Elevenlabs

# DataBase
engine = create_engine(DatabaseUri)

# Create the table
Base.metadata.create_all(engine)

# reddit = Reddit()
# print (reddit.parse_threads("AskReddit", 2024, 11, 10))

# elevenlabs = Elevenlabs()
# print (elevenlabs.generate("Beethoven, the dog, and Beethoven, the composer, aren’t actually the same person."))