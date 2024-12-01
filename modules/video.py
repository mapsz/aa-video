from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from moviepy.config import change_settings
from modules import make_dir
from PIL import Image
import time
import os
import yt_dlp

from PIL import Image
change_settings({"FFMPEG_BINARY": "libs/ffmpeg.exe"})

class Video:
    def yt_dlp_select_format(ctx):
        formats = ctx.get('formats')[::-1]

        best_video = False
        best_audio = False
        for format in formats:
            if "height" in format and format["video_ext"] == "mp4":
                if (best_video == False): best_video = format
                if(format["height"] == 1080):
                    best_video = format

                if (format["height"] > best_video["height"] and best_video["height"] != 1080):
                    best_video = format

            if not "height" in format and format["audio_ext"] == "mp4":
                if (best_audio == False): best_audio = format
                if (best_audio["quality"] > best_audio["quality"]):
                    best_audio = format

        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }

    def yt_download(url, video_filepath):
        ydl_opts = {
            'format': Video.yt_dlp_select_format,
            'outtmpl': video_filepath,
            # 'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    def split_video(video_filepath, chunk_length=60):
        with VideoFileClip(video_filepath) as video:
            video_duration = video.duration

        start_time = 0
        chunk_number = 1
        video_filename = os.path.splitext(os.path.basename(video_filepath))[0]
        while start_time < video_duration:
            end_time = min(start_time + chunk_length, video_duration)
            output_filepath = f"storage/video/60/{video_filename}_{chunk_number}.mp4"
            make_dir(output_filepath)
            ffmpeg_extract_subclip(video_filepath, start_time, end_time, output_filepath)
            print(f"Video created: {output_filepath}")
            start_time += chunk_length
            chunk_number += 1

    def to_vertical(video_filepath):
        with VideoFileClip(video_filepath) as video:
            width, height = video.size

            new_width = int(height * 9 / 16)
            if new_width % 2 != 0: new_width -= 1

            video_resized = video.crop(
                x1=(width - new_width) // 2,
                x2=(width + new_width) // 2
            )

            video_filename = os.path.splitext(os.path.basename(video_filepath))[0]

            filepath = f"storage/video/sourceVertical/{video_filename}.mp4"
            make_dir(filepath)

            video_resized.write_videofile(
                filepath,
                codec="libx264",
                audio_codec="aac",
                ffmpeg_params=[
                    "-pix_fmt", "yuv420p"
                ]
            )

    def overlay_audio(video_filepath, audio_filepath):
        # Загрузка аудио
        video = VideoFileClip(video_filepath)

        # Загрузка аудио
        audio = AudioFileClip(audio_filepath)

        # Установка аудио в видео
        video_with_audio = video.set_audio(audio)

        # Сохранение результата

        filepath = f"storage/video/60/with_audio/{os.path.splitext(os.path.basename(video_filepath))[0]}_{os.path.splitext(os.path.basename(audio_filepath))[0]}.mp4"
        make_dir(filepath)
        video_with_audio.write_videofile(filepath)

    def overlay_thread_images(video_filepath, thread, thread_timing):
        video = VideoFileClip(video_filepath)
        pause = True
        thread_title = True
        current_duration = 0
        images = []
        i = 0
        for thread_time in thread_timing:
            if pause:
                pause = False
                current_duration += thread_time
                continue

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
            pause = True

        final = CompositeVideoClip([video] + images)
        filepath = f"storage/video/60/final/{os.path.splitext(os.path.basename(video_filepath))[0]}.mp4"
        make_dir(filepath)
        final.write_videofile(filepath)

        return filepath