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
            if "width" in format and format["video_ext"] == "mp4":
                if (best_video == False): best_video = format
                if (format["width"] > best_video["width"]):
                    best_video = format

            if not "width" in format and format["audio_ext"] == "mp4":
                if (best_audio == False): best_audio = format
                if (best_audio["quality"] > best_audio["quality"]):
                    best_audio = format

        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }

    def yt_download(url, filepath):
        ydl_opts = {
            'format': Video.yt_dlp_select_format,
            'outtmpl': filepath,
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

    def to_vertical(video_path):
        with VideoFileClip(video_path) as video:
            width, height = video.size

            new_width = int(height * 9 / 16)
            video_resized = video.crop(x1=(width - new_width) // 2, x2=(width + new_width) // 2)

            filepath = f"storage/{time.time()}.mp4"

            video_resized.write_videofile(
                filepath,
            )

    def overlay_audio(video_filepath, audio_filepath):
        # Загрузка аудио
        video = VideoFileClip(video_filepath)

        # Загрузка аудио
        audio = AudioFileClip(audio_filepath)

        # Установка аудио в видео
        video_with_audio = video.set_audio(audio)

        # Сохранение результата
        video_with_audio.write_videofile("output_video.mp4")

    def overlay_thread_images(video_filepath, thread, thread_timing):
        # Загрузка видео
        video = VideoFileClip(video_filepath)

        # Путь к файлу изображения
        thread_filepath = f"storage/images/threads/{thread.identifier}.png"

        # Переменные
        pause = True
        thread_title = True
        current_duration = 0
        images = []

        # Работа с временными файлами
        for thread_time in thread_timing:
            current_duration += thread_time
            if pause:
                pause = False
                continue

            if thread_title:
                thread_title = False
                image_filepath = thread_filepath
            else:
                continue

            # Ресайз изображения только один раз
            image = Image.open(image_filepath)
            new_width = video.size[0]
            original_width, original_height = image.size
            aspect_ratio = original_height / original_width
            new_height = int(new_width * aspect_ratio)
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            temp_image = f"storage/temp/{thread.identifier}_resized.png"
            make_dir(temp_image)
            resized_image.save(temp_image)

            # Добавление изображения в список
            image_clip = ImageClip(temp_image)
            image_clip = image_clip.set_start(current_duration / 1000)  # Время в секундах
            image_clip = image_clip.set_duration(thread_time / 1000)
            image_clip = image_clip.set_position(("center", "top"))
            images.append(image_clip)

        # Создание финального видео
        final = CompositeVideoClip([video] + images)

        # Сохранение результата
        output_filepath = video_filepath.replace(".mp4", "_with_overlay.mp4")
        final.write_videofile(
            output_filepath,
            # codec="h264_nvenc",  # Используем NVENC
            # ffmpeg_params=[
            #     "-preset", "lossless",
            # ]
        )

        return output_filepath