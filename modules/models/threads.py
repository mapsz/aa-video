from sqlalchemy import Column, Integer, String, DateTime
from ._base import Base
from datetime import datetime

class Threads(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    author = Column(String)
    score = Column(Integer)
    title = Column(String)
    symbol_count = Column(Integer)
    date = Column(DateTime)

def __repr__(self):
    return (
        f"<Threads("

        f"id={self.id},"
        f"identifier='{self.identifier}', "
        f"author='{self.author}', "
        f"score={self.score}, "
        f"title='{self.title}', "
        f"symbol_count={self.symbol_count}, "
        f"date='{self.date}') "

        f">"
    )