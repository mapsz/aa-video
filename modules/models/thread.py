from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.exc import IntegrityError
from ._base import Base
from .association import thread_video_association

class Thread(Base):
    __tablename__ = 'threads'

    REDDIT = "reddit"

    id = Column(Integer, primary_key=True)
    source = Column(String)
    identifier = Column(String)
    author = Column(String)
    score = Column(Integer)
    title = Column(String)
    symbol_count = Column(Integer)
    date = Column(DateTime)

    # Many-to-many relationship with Video
    videos = relationship(
        "Video",
        secondary=thread_video_association,
        back_populates="threads"
    )

    def __repr__(self):
        return (
            f"<Thread("
            f"id={self.id},"
            f"source='{self.source}', "
            f"identifier='{self.identifier}', "
            f"author='{self.author}', "
            f"score={self.score}, "
            f"title='{self.title}', "
            f"symbol_count={self.symbol_count}, "
            f"date='{self.date}') "
            f">"
        )

    @classmethod
    def get(cls, session, thread_id):
        return session.query(cls).options(joinedload(cls.comments)).filter(cls.id == thread_id).one_or_none()

    def calculate_symbol_count(thread):
        symbol_count = len(thread.title)

        for comment in thread.comments:
            symbol_count += len(comment.text)

        thread.symbol_count = symbol_count

        return thread

    def add_if_not_exists(session, thread):
        exists = session.query(Thread).filter_by(
            source=thread.source,
            identifier=thread.identifier,
        ).first()

        if not exists:
            try:
                session.add(thread)
                session.commit()
            except IntegrityError:
                session.rollback()

            return thread
        else:
            return exists

    def get_unused(session):
        query = text(
            "SELECT t.* "
            "FROM threads t "
            "LEFT JOIN thread_video_association tv "
            "ON t.id = tv.thread_id "
            "WHERE tv.thread_id IS NULL "
        )
        return session.execute(query)

