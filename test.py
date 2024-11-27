from annotated_types import T
from config import DatabaseUri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.models._base import Base
from modules.models import Thread
from modules import Reddit
from datetime import datetime
import textwrap
from PIL import ImageFont, ImageDraw, Image
from modules import ComicBubble
from modules import get_session, make_dir
from modules import Elevenlabs
from modules import TextToSpeech
from pydub import AudioSegment
from pydub.utils import which
from modules import Video
from modules import make_dir
from moviepy.config import change_settings



# filepath = "storage/video/source"
# make_dir(filepath)
# Video.yt_download("https://www.youtube.com/watch?v=r0hFL14JGyU", "r0hFL14JGyU")

thread = Thread()
thread = thread.get(get_session(), 4)

# comic_bubble = ComicBubble()
# comic_bubble.thread_to_images(thread)

thread_timing = TextToSpeech.get_thread_timing(thread)
Video.overlay_thread_images("storage/video/60/VS3D8bgYhf4_1.mp4", thread, thread_timing)




# change_settings({"FFMPEG_BINARY": "libs/ffmpeg.exe"})

# print(get_setting("FFMPEG_BINARY"))

# Video.split_video(f"storage/video/sourceVertical/VS3D8bgYhf4.mp4")
# Video.to_vertical(f"storage/video/source/source.mp4")
# Video.yt_download("https://www.youtube.com/watch?v=VS3D8bgYhf4", "storage/video/source")

# Video.overlay_audio(f"storage/video/60/VS3D8bgYhf4_1.mp4", f"storage/audio/threads/full/1go8oqk.mp3")

# print(thread_timing)