from sqlalchemy import Column, Integer, String, DateTime, text
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

    STATUS_READY = "ready"

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

    def get_unused(session, duration):
        query = text(
            f"SELECT v.* "
            f"FROM videos v "
            f"LEFT JOIN videos sv "
                f"ON sv.identifier = v.identifier "
                f"AND sv.source = v.source "
                f"AND sv.part = v.part "
                f"AND sv.duration = v.duration "
                f"AND sv.\"type\" = :type_final "
            f"WHERE v.source = :source_youtube "
                f"AND v.\"type\" = :type_source_splited "
                f"AND v.duration = :duration "
                f"AND sv.identifier IS NULL "
        )
        return session.execute(
            query,
            {
                'type_final': Video.TYPE_FINAL,
                'source_youtube': Video.SOURCE_YOUTUBE,
                'type_source_splited': Video.TYPE_SOURCE_SPLITED,
                'duration': duration,
            }
        )
