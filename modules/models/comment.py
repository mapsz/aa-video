from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ._base import Base
from .threads import Threads
from datetime import datetime

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('threads.id'))
    identifier = Column(String)
    author = Column(String)
    score = Column(Integer)
    text = Column(String)
    symbol_count = Column(Integer)
    date = Column(DateTime)

    threads = relationship("Threads", back_populates="comments")

def __repr__(self):
    return (
        f"<Comment("

        f"id={self.id},"
        f"thread_id={self.thread_id},"
        f"identifier='{self.identifier}', "
        f"author='{self.author}', "
        f"score={self.score}, "
        f"text='{self.text}', "
        f"symbol_count={self.symbol_count}, "
        f"date='{self.date}') "

        f">"
    )

# Relationships
Threads.comments = relationship("Comment", order_by=Comments.id, back_populates="thread")