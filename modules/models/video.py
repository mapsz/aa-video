from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ._base import Base
from .association import thread_video_association

class Video(Base):
    __tablename__ = 'videos'

    SOURCE_YOUTUBE = "youtube"

    TYPE_SOURCE = "source"
    TYPE_SOURCE_VERTICAL = "source_vertical"
    TYPE_SOURCE_SPLITED_60 = "source_splited_60"
    TYPE_SOURCE_SPLITED_90 = "source_splited_90"
    TYPE_SOURCE_SPLITED_120 = "source_splited_120"

    id = Column(Integer, primary_key=True)
    source = Column(String)
    identifier = Column(String)
    type = Column(String)
    filepath = Column(String)
    part = Column(Integer)
    date = Column(DateTime)

    # Many-to-many relationship with Thread
    threads = relationship(
        "Thread",
        secondary=thread_video_association,
        back_populates="videos"
    )

    def __repr__(self):
        return (
            f"<Video("
            f"id={self.id},"
            f"source='{self.source}', "
            f"identifier='{self.identifier}', "
            f"type='{self.type}', "
            f"filepath='{self.filepath}', "
            f"part={self.part}, "
            f"date='{self.date}') "
            f">"
        )