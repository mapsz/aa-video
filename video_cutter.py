from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def split_video(input_video, output_folder, chunk_length=60):
    import os
    from moviepy.editor import VideoFileClip

    # Загружаем видео
    video = VideoFileClip(input_video)
    video_duration = video.duration  # Получаем продолжительность видео в секундах

    # Разбиваем видео по частям
    start_time = 0
    chunk_number = 1
    while start_time < video_duration:
        end_time = min(start_time + chunk_length, video_duration)  # Убедимся, что конец не выходит за длительность видео
        output_file = os.path.join(output_folder, f"chunk_{chunk_number}.mp4")
        ffmpeg_extract_subclip(input_video, start_time, end_time, targetname=output_file)
        print(f"Создано видео: {output_file}")
        start_time += chunk_length
        chunk_number += 1

# Пример использования:
input_video = "storage/videos/full/video.mp4"  # Путь к вашему видео
output_folder = "storage/videos/minute"    # Папка для сохранения отрезков
split_video(input_video, output_folder)
