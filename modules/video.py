from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import time
import os
import yt_dlp

class Video:
    def yt_dlp_select_format(ctx):
        formats = ctx.get('formats')[::-1]

        best_video = next(f for f in formats
                        if f['vcodec'] != 'none' and f['acodec'] == 'none')

        audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
        best_audio = next(f for f in formats if (
            f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

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
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

# class video_cutter:
#     def __init__(self, input_video, output_folder):
#         self.input_video = input_video
#         self.output_folder = output_folder

#     def split_video(vertical_video, chunk_length=60):
#         video = VideoFileClip(vertical_video)
#         video_duration = video.duration

#         start_time = 0
#         chunk_number = 1
#         while start_time < video_duration:
#             end_time = min(start_time + chunk_length, video_duration)  # Убедимся, что конец не выходит за длительность видео
#             output_file = os.path.join(self.output_folder, f"chunk_{chunk_number}.mp4")
#             ffmpeg_extract_subclip(vertical_video, start_time, end_time, targetname=output_file)
#             print(f"Создано видео: {output_file}")
#             start_time += chunk_length
#             chunk_number += 1

#     def video_vertical(self):
#         # Загрузите видео
#         video = VideoFileClip(self.input_video)

#         # Рассчитаем новые размеры
#         width, height = video.size
#         new_width = int(height * 9 / 16)

#         # Обрезаем по бокам
#         video_resized = video.crop(x1=(width - new_width) // 2, x2=(width + new_width) // 2)

#         # Сохраняем результат
#         filepath = (f"storage/temp/{time.time()}.mp4")
#         video_resized.write_videofile(filepath)

#         return filepath

#     def cut(self, vertical=true):
#         if vertical:
#             vertical_video = self.video_vertical()
#         else:
#             vertical_video = self.input_video
#         split_video(vertical_video)
