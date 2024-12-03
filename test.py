from annotated_types import T
from config import DatabaseUri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.models._base import Base
from modules.models import Thread
from modules.models import Comment
from modules.models import Video
from modules import Reddit
from datetime import datetime
import textwrap
import os
import time
from PIL import ImageFont, ImageDraw, Image
from modules import ComicBubble
from modules import get_session, make_dir
from modules import Elevenlabs
from modules import TextToSpeech, VideoManager
from pydub import AudioSegment
from pydub.utils import which
from modules import make_dir
from moviepy.config import change_settings

session = get_session()

while 1:
    # Youtube Videos Download
    VideoManager.files_to_db(session)

    videos = session.query(Video).filter_by(
        source=Video.SOURCE_YOUTUBE,
        type=Video.TYPE_SOURCE,
        filepath=None,
    ).all()

    for video in videos:
        VideoManager.yt_download(VideoManager.identifier_to_yt_url(video.identifier))

    VideoManager.files_to_db(session)

    # Source Videos To Vertical
    videos = session.query(Video).filter(
        Video.source == Video.SOURCE_YOUTUBE,
        Video.type == Video.TYPE_SOURCE,
        Video.filepath.isnot(None)
    ).all()

    for video in videos:
        existing_video = session.query(Video).filter_by(
            source=Video.SOURCE_YOUTUBE,
            identifier=video.identifier,
            type=Video.TYPE_SOURCE_VERTICAL
        ).first()

        if existing_video: continue

        VideoManager.to_vertical(video)

    VideoManager.files_to_db(session)

    # Source Vertical Videos Split
    videos = session.query(Video).filter(
        Video.source == Video.SOURCE_YOUTUBE,
        Video.type == Video.TYPE_SOURCE_VERTICAL,
        Video.filepath.isnot(None)
    ).all()

    types = [
        Video.TYPE_SOURCE_SPLITED_60,
        Video.TYPE_SOURCE_SPLITED_90,
        Video.TYPE_SOURCE_SPLITED_120,
    ]

    for _type in types:
        for video in videos:
            existing_video = session.query(Video).filter_by(
                source=Video.SOURCE_YOUTUBE,
                identifier=video.identifier,
                type=_type,
            ).first()

            if existing_video: continue

            VideoManager.split_video(video, _type)

    VideoManager.files_to_db(session)

    # Update Threads
    if (datetime.now() - Comment.get_last_comment_date(session)).total_seconds() / 3600 > 24:
        reddit = Reddit()
        threads = reddit.fetch_top_threads("AskReddit")

        saved_threads = []
        for thread in threads:
            saved_threads.append(Thread.add_if_not_exists(session, thread))
        threads = saved_threads

        for thread in threads:
            comments = reddit.fetch_popular_comments(thread)
            for comment in comments:
                Comment.add_if_not_exists(session, comment, thread.id)

    # threads to images

    # threads to audio

    # video with audio

    # video with audio to final

    exit()
    time.sleep(1)


# print (VideoManager.identifier_from_yt_url("https://www.youtube.com/watch?v=WA71h4m5Zpg"))











# filepath = "storage/video/source"
# make_dir(filepath)

# if not os.path.exists("storage/video/source/LZWfD_cO3cc.mp4"):
#     Video.yt_download("https://www.youtube.com/watch?v=LZWfD_cO3cc", "storage/video/source/LZWfD_cO3cc")


# Video.to_vertical(f"storage/video/source/LZWfD_cO3cc.mp4")
# Video.split_video(f"storage/video/sourceVertical/LZWfD_cO3cc.mp4")




# session = get_session()


# thread = Thread()
# thread = thread.get(session, 9)

# # Example usage
# # thread = Thread(source="reddit", identifier="123", author="user1", title="Sample Thread")
# video = Video(source="youtube", identifier="456", type="mp4", filepath="/path/to/video")

# # Associate them
# thread.videos.append(video)

# # Commit to database
# session.add(thread)
# session.commit()

# # Access relationships
# print(thread.videos)  # List of associated videos
# print(video.threads)  # List of associated threads

# TextToSpeech.thread_to_audios(thread)
# TextToSpeech.make_full_thread_audio(thread)

# comic_bubble = ComicBubble()
# comic_bubble.thread_to_images(thread)

# # Video.overlay_audio(f"storage/video/60/LZWfD_cO3cc_1.mp4", f"storage/audio/threads/full/1gq1rw6.mp3")

# thread_timing = TextToSpeech.get_thread_timing(thread)
# Video.overlay_thread_images(f"storage/video/60/with_audio/LZWfD_cO3cc_1_1gq1rw6.mp4", thread, thread_timing)




# change_settings({"FFMPEG_BINARY": "libs/ffmpeg.exe"})

# print(get_setting("FFMPEG_BINARY"))



# Video.yt_download("https://www.youtube.com/watch?v=WA71h4m5Zpg")

# Video.overlay_audio(f"storage/video/60/VS3D8bgYhf4_1_with_overlay.mp4", f"storage/audio/threads/full/1go8oqk.mp3")

# print(thread_timing)