from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, desc
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from ._base import Base
from modules.models import Thread
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

    thread = relationship("Thread", back_populates="comments")

    def __repr__(self):
        return (
            f"<Comment("
            f"id={self.id}, "
            f"thread_id={self.thread_id}, "
            f"identifier='{self.identifier}', "
            f"author='{self.author}', "
            f"score={self.score}, "
            f"text='{self.text}', "
            f"symbol_count={self.symbol_count}, "
            f"date='{self.date}')>"
        )

    def add_if_not_exists(session, comment, thread_id):
        exists = session.query(Comment).filter_by(
            thread_id=thread_id,
            identifier=comment.identifier,
        ).first()

        if not exists:
            try:
                session.add(comment)
                session.commit()
            except IntegrityError:
                session.rollback()

            return comment
        else:
            return exists

    def get_last_comment_date(session):
        last_comment = session.query(Comment).order_by(desc(Comment.date)).first()

        if last_comment:
            return last_comment.date
        else:
            return None

#Relationships
Thread.comments = relationship("Comment", order_by=Comment.id, back_populates="thread")
