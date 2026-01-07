from annotated_types import T
from modules.models import Thread
from modules.models import Comment
from modules.models import Video
from modules import Reddit
from datetime import datetime
import copy
import os
import time
from modules import ComicBubble
from modules import get_session
from modules import TextToSpeech, VideoManager, ThreadManager
from mutagen.mp3 import MP3

from modules.utils.helpers import dd


def test_current_comments_symbols_per_sec(session):
    directory = f"storage/audio/comments"
    items = os.listdir(directory)
    files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
    count = 0
    all = 0
    max = 0
    min = 999
    for file in files:
        identifier = file.replace(".mp3", "")
        length = MP3(f"{directory}/{file}").info.length
        comment = session.query(Comment).filter(Comment.identifier == identifier).first()
        if comment == None: continue
        text = ThreadManager.filter_text(comment.text)
        if ThreadManager.is_bad_text(text): continue
        text_lenght = ThreadManager.get_adjusted_text_symbols(text)
        per_sec = text_lenght / length
        all += per_sec
        count += 1
        max = per_sec if per_sec > max else max
        min = per_sec if per_sec < min else min
        print(f"{identifier} - {per_sec} - {length}")

    print("===")
    print(f"max - {max}")
    print(f"min - {min}")
    print(all / count)
    exit()


session = get_session()

# test_current_comments_symbols_per_sec(session)

while 1:
    durations = [
        Video.DURATION_60,
        # Video.DURATION_90,
        # Video.DURATION_120,
    ]

    # Youtube Videos Download
    if 1:
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
    if 1:
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
    if 1:
        videos = session.query(Video).filter(
            Video.source == Video.SOURCE_YOUTUBE,
            Video.type == Video.TYPE_SOURCE_VERTICAL,
            Video.filepath.isnot(None)
        ).all()

        for duration in durations:
            for video in videos:
                existing_video = session.query(Video).filter_by(
                    source=Video.SOURCE_YOUTUBE,
                    identifier=video.identifier,
                    type=Video.TYPE_SOURCE_SPLITED,
                    duration=duration,
                ).first()

                if existing_video: continue

                VideoManager.split_video(video, duration)

        VideoManager.files_to_db(session)

    dd(11)

    # Update Threads
    if 1:
        last_comment_date = Comment.get_last_comment_date(session)
        if (last_comment_date is None or
                (datetime.now() - last_comment_date).total_seconds() / 3600 > 24):
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

    # Get Unused Thread And Video
    if 1:
        # Get Unused Threads
        threads = list(Thread.get_unused(session))
        if len(threads) == 0:
            print("no unused threads")
            exit()
        thread = threads[0]

        # Get unused videos
        videos = {}
        for duration in durations:
            _videos = list(Video.get_unused(session, duration))
            if len(_videos) == 0:
                print(f"no unused {duration} video")
                exit()
            videos[duration] = _videos[0]

    # Pick comments by seconds
    if 1:
        durationThreads = {}
        baseThread = Thread().get(session, thread.id)
        for duration in durations:
            thread = copy.deepcopy(baseThread)
            comments, total_length = ThreadManager.pick_thread_by_max_seconds(
                thread, duration
            )
            thread.comments = comments
            durationThreads[duration] = thread

    # To mp3s
    if 1:
        for key, thread in durationThreads.items():
            TextToSpeech.thread_to_audios(thread)

    # Adjust
    if 1:
        adjustedDurationThreads = {}
        for duration, thread in durationThreads.items():
            adjustedThread = thread
            adjust = 0
            banned_comments = []
            while 1:
                if adjust > 5:
                    banned_comments.append(
                        ThreadManager.get_most_stand_out_comment(
                            adjustedThread
                        )
                    )
                    adjust = 0

                adjusting = TextToSpeech.adjust_comments_by_duration(
                    adjustedThread, duration
                )
                if adjusting is True:
                    break
                if adjusting == "+":
                    new_duration = duration + adjust
                if adjusting == "-":
                    new_duration = duration - adjust

                adjustedThread = copy.deepcopy(Thread().get(session, thread.id))

                comments, total_length = (
                    ThreadManager.pick_thread_by_max_seconds(
                        adjustedThread, new_duration, banned_comments
                    )
                )
                adjustedThread.comments = comments
                TextToSpeech.thread_to_audios(adjustedThread)

                print(
                    f"adjusting - {round(adjust, 1)} - "
                    f"{adjustedThread.identifier} - {duration}"
                    f"\nBanned comments: {banned_comments}"
                    f"\n=====\n"
                )
                TextToSpeech.thread_to_audios(thread)
                adjust += 0.1
                time.sleep(1)

            adjustedDurationThreads[duration] = adjustedThread

        durationThreads = adjustedDurationThreads

    # Make Full mp3s
    for duration, thread in durationThreads.items():
        TextToSpeech.make_full_thread_audio(thread, duration)

    # Make Images
    if 1:
        for duration, thread in durationThreads.items():
            comic_bubble = ComicBubble()
            comic_bubble.thread_to_images(thread)

    #
    for duration, thread in durationThreads.items():
        length, map = TextToSpeech.get_thread_audios_lenght(thread)
        pause = TextToSpeech.get_thread_suitable_pauses_lenght(
            thread, duration
        )
        video_clip = VideoManager.create_video_clip(videos[duration].filepath)
        video_clip = VideoManager.overlay_audio(
            video_clip,
            f"storage/audio/threads/full/{duration}/{thread.identifier}.mp3"
        )
        video_clip = VideoManager.overlay_thread_images(
            video_clip,
            thread,
            map,
            pause
        )
        filepath = (
            f"storage/video/final/{duration}/"
            f"{videos[duration].identifier}_{thread.identifier}.mp4"
        )
        VideoManager.write(video_clip, filepath)
        VideoManager.close_video_clip(video_clip)

        video = Video(
            source=videos[duration].source,
            identifier=videos[duration].identifier,
            part=videos[duration].part,
            type=Video.TYPE_FINAL,
            filepath=filepath,
            duration=duration,
            status=Video.STATUS_READY,
        )
        threadModul = Thread()
        threadModul = threadModul.get(session, thread.id)
        video.threads.append(threadModul)
        session.add(video)
        session.commit()

    # exit()
    time.sleep(1)
