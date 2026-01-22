from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from moviepy.config import change_settings
from modules import make_dir
from modules.models import Video
from PIL import Image
from urllib.parse import urlparse, parse_qs
import os, glob, yt_dlp, re


from PIL import Image
change_settings({"FFMPEG_BINARY": "libs/ffmpeg.exe"})

class VideoManager:
    def files_to_db(session):
        for root, dirs, files in os.walk(f"storage/video"):
            for file in files:
                file_path = os.path.join(root, file)
                filename, file_ext = os.path.splitext(file_path)
                filename = os.path.basename(filename)
                if file_ext != ".mp4":
                    continue
                folders = os.path.dirname(file_path).split(os.sep)
                folders = [folder for folder in folders if folder not in ['storage', 'video', 'storage/video']]
                _type = folders[0]
                source = folders[1]
                duration = folders[2] if len(folders) > 2 else None

                if _type == "final":
                    continue

                part = None
                identifier = re.sub(r"__part_\d+__", "", filename)
                match = re.search(r"__part_(\d+)__", file)
                if match: part = int(match.group(1))

                existing_video = session.query(Video).filter_by(
                    identifier=identifier,
                    type=_type,
                    source=source,
                    duration=duration,
                    part=part,
                    filepath=file_path,
                ).first()

                if existing_video: continue

                no_path_video = session.query(Video).filter_by(
                    identifier=identifier,
                    type=_type,
                    source=source,
                    duration=duration,
                    part=part,
                    filepath=None,
                ).first()

                if no_path_video:
                    no_path_video.filepath = file_path
                    continue

                video = Video(
                    identifier=identifier,
                    type=_type,
                    source=source,
                    duration=duration,
                    part=part,
                    filepath=file_path,
                )
                session.add(video)
                print(f"path - {file_path}; type - {_type}; source - {source}; duration - {duration}; identifier - {identifier};  file_ext - {file_ext};  part - {part}")

        session.commit()

    def identifier_from_yt_url(url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        identifier = query_params.get('v', [None])[0]
        if identifier:
            return identifier
        else:
            raise ValueError("The 'v' parameter is missing in the URL")

    def identifier_to_yt_url(identifier):
        return f"https://www.youtube.com/watch?v={identifier}"

    def add_yt_video(identifier, session):
        existing_video = session.query(Video).filter_by(
            source=Video.SOURCE_YOUTUBE,
            identifier=identifier,
            type=Video.TYPE_SOURCE
        ).first()

        if not existing_video:
            video = Video(
                source=Video.SOURCE_YOUTUBE,
                identifier=identifier,
                type=Video.TYPE_SOURCE,
            )
            session.add(video)
            session.commit()
            return video
        else:
            return existing_video

    def yt_dlp_select_format(ctx):
        formats = ctx.get('formats')[::-1]

        best_height = False
        for format in formats:
            if "height" in format and format.get("video_ext") in ["mp4", "webm", "mkv"]:
                if (best_height == False): best_height = format["height"]
                if (format["height"] == 1080):
                    best_height = format["height"]

                if (best_height != 1080 and format["height"] > best_height):
                    best_height = format["height"]

        best_video = False
        for format in formats:
            if "height" in format and format.get("video_ext") in ["mp4", "webm", "mkv"]:
                if (best_video == False): best_video = format
                if (format["height"] == best_height and
                    format.get("vbr") is not None and
                    best_video.get("vbr") is not None and
                    format["vbr"] > best_video["vbr"]):
                    best_video = format

        best_audio = False
        for format in formats:
            if "height" not in format and format.get("audio_ext") in ["m4a", "mp3", "webm", "opus"]:
                if (best_audio == False): best_audio = format
                if (format.get("quality") is not None and
                    best_audio.get("quality") is not None and
                    format["quality"] > best_audio["quality"]):
                    best_audio = format

        # Validate that both video and audio formats were found
        if best_video == False or best_audio == False:
            return None

        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }

    def yt_download(url):
        filename = VideoManager.identifier_from_yt_url(url)
        filepath = f"storage/video/source/{Video.SOURCE_YOUTUBE}/{filename}.mp4"
        make_dir(filepath)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'format_sort': ['res:1080', 'vbr', 'abr'],
            'outtmpl': filepath,
            'postprocessors': [
                {'key': 'FFmpegMetadata'}
            ],
            'prefer_ffmpeg': True,
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    def split_video(videoModel, duration):
        chunk_length = duration
        with VideoFileClip(videoModel.filepath) as video:
            video_duration = video.duration

        start_time = 0
        chunk_number = 1
        video_filename = os.path.splitext(os.path.basename(videoModel.filepath))[0]
        while start_time < video_duration:
            end_time = start_time + chunk_length
            if (end_time > video_duration):
                return
            output_filepath = f"storage/video/{Video.TYPE_SOURCE_SPLITED}/{Video.SOURCE_YOUTUBE}/{duration}/{video_filename}__part_{chunk_number}__.mp4"
            make_dir(output_filepath)
            ffmpeg_extract_subclip(videoModel.filepath, start_time, end_time, output_filepath)
            start_time += chunk_length
            chunk_number += 1

    def to_vertical(videoModel):
        with VideoFileClip(videoModel.filepath) as video:
            width, height = video.size

            new_width = int(height * 9 / 16)
            if new_width % 2 != 0: new_width -= 1

            video_resized = video.crop(
                x1=(width - new_width) // 2,
                x2=(width + new_width) // 2
            )

            video_filename = os.path.splitext(os.path.basename(videoModel.filepath))[0]

            filepath = f"storage/video/{Video.TYPE_SOURCE_VERTICAL}/{Video.SOURCE_YOUTUBE}/{video_filename}.mp4"
            make_dir(filepath)

            VideoManager.write(video_resized, filepath)

    def overlay_audio(video, audio_filepath):
        # Загрузка аудио
        # video = VideoFileClip(video_filepath)

        # Загрузка аудио
        audio = AudioFileClip(audio_filepath)

        # Установка аудио в видео
        return video.set_audio(audio)
        # video_with_audio = video.set_audio(audio)

        # Сохранение результата

        # filepath = f"storage/video/60/with_audio/{os.path.splitext(os.path.basename(video_filepath))[0]}_{os.path.splitext(os.path.basename(audio_filepath))[0]}.mp4"
        # make_dir(filepath)
        # video_with_audio.write_videofile(filepath)

    def overlay_thread_images(video, thread, thread_timing, pause_time):
        thread_title = True
        current_duration = 0
        images = []
        i = 0
        print(len(thread.comments))
        print(thread_timing)
        current_duration += pause_time
        for thread_time in thread_timing:
            if thread_title:
                thread_title = False
                image_filepath = f"storage/images/threads/{thread.identifier}.png"
            else:
                image_filepath = f"storage/images/comments/{thread.comments[i].identifier}.png"
                i += 1

            print(f"{current_duration} - {thread_time}")

            # Resize image
            image = Image.open(image_filepath)
            new_width = int(video.size[0] * 0.95)
            original_width, original_height = image.size
            aspect_ratio = original_height / original_width
            new_height = int(new_width * aspect_ratio)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            temp_image = f"storage/temp/{thread.identifier}_resized.png"
            make_dir(temp_image)
            resized_image.save(temp_image)

            # Add image
            image_clip = ImageClip(temp_image)
            image_clip = image_clip.set_start(current_duration / 1000)  # Время в секундах
            image_clip = image_clip.set_duration(thread_time / 1000)
            image_clip = image_clip.set_position(("center", "center"))
            images.append(image_clip)

            current_duration += thread_time
            current_duration += pause_time

        return CompositeVideoClip([video] + images)
        # final = CompositeVideoClip([video] + images)
        # filepath = f"storage/video/60/final/{os.path.splitext(os.path.basename(video_filepath))[0]}.mp4"
        # make_dir(filepath)
        # final.write_videofile(filepath)

        # return filepath

    def write(video, filepath):
        make_dir(filepath)
        video.write_videofile(
            filepath,
            codec="libx264",
            audio_codec="aac",
            fps=video.fps,
            preset="slow",
            # ffmpeg_params=["-crf", "0"],
        )

    def create_video_clip(video_filepath):
        return VideoFileClip(video_filepath)

    def close_video_clip(video_clip):
        video_clip.close()
