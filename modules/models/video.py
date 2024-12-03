from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ._base import Base
from .association import thread_video_association

class Video(Base):
    __tablename__ = 'videos'

    SOURCE_YOUTUBE = "youtube"

    TYPE_SOURCE = "source"
    TYPE_SOURCE_VERTICAL = "source_vertical"
    TYPE_SOURCE_SPLITED = "source_splited"
    TYPE_FINAL = "final"

    DURATION_60 = 60
    DURATION_90 = 90
    DURATION_120 = 120

    id = Column(Integer, primary_key=True)
    source = Column(String)
    identifier = Column(String)
    type = Column(String)
    duration = Column(Integer)
    status = Column(String)
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
            f"duration='{self.type}', "
            f"status='{self.status}', "
            f"filepath='{self.filepath}', "
            f"part={self.part}, "
            f"date='{self.date}') "
            f">"
        )