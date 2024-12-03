from sqlalchemy import Table, Column, Integer, ForeignKey
from ._base import Base

thread_video_association = Table(
    'thread_video_association',
    Base.metadata,
    Column('thread_id', Integer, ForeignKey('threads.id'), primary_key=True),
    Column('video_id', Integer, ForeignKey('videos.id'), primary_key=True)
)