from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import time
import os

class video_cutter:
    def __init__(self, input_video, output_folder):
        self.input_video = input_video
        self.output_folder = output_folder

    def split_video(vertical_video, chunk_length=60):
        video = VideoFileClip(vertical_video)
        video_duration = video.duration

        start_time = 0
        chunk_number = 1
        while start_time < video_duration:
            end_time = min(start_time + chunk_length, video_duration)  # Убедимся, что конец не выходит за длительность видео
            output_file = os.path.join(self.output_folder, f"chunk_{chunk_number}.mp4")
            ffmpeg_extract_subclip(vertical_video, start_time, end_time, targetname=output_file)
            print(f"Создано видео: {output_file}")
            start_time += chunk_length
            chunk_number += 1

    def video_vertical():
        # Загрузите видео
        video = VideoFileClip(input_video)

        # Рассчитаем новые размеры
        width, height = video.size
        new_width = int(height * 9 / 16)

        # Обрезаем по бокам
        video_resized = video.crop(x1=(width - new_width) // 2, x2=(width + new_width) // 2)

        # Сохраняем результат
        filepath = (f"storage/temp/{time.time()}.mp4")
        video_resized.write_videofile(filepath)

        return filepath

    def cut(vertical=true):
        if vertical:
            vertical_video = self.video_vertical()
        else:
            vertical_video = self.input_video
        split_video(vertical_video)
