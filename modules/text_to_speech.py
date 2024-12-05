from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from config import min_pause, max_pause
from numpy import append
from config import elevenlabs_config
from modules.models import thread
from modules import make_dir
from mutagen.mp3 import MP3
from pydub import AudioSegment
from pydub.utils import which
import os

class TextToSpeech:
    def thread_to_audios(thread):
        elevenlabs = Elevenlabs()

        filepath = f"storage/audio/threads/{thread.identifier}.mp3"
        if not os.path.exists(filepath):
            make_dir(filepath)
            elevenlabs.generate(thread.title, filepath)

        for comment in thread.comments:
            filepath = f"storage/audio/comments/{comment.identifier}.mp3"
            if not os.path.exists(filepath):
                make_dir(filepath)
                elevenlabs.generate(comment.text, filepath)

    def get_thread_audios_lenght(thread):
        length = 0
        map = []
        filepath = f"storage/audio/threads/{thread.identifier}.mp3"
        if os.path.exists(filepath):
            audio = MP3(filepath)
            length += audio.info.length * 1000
            map.append(audio.info.length * 1000)

        for comment in thread.comments:
            filepath = f"storage/audio/comments/{comment.identifier}.mp3"
            if os.path.exists(filepath):
                audio = MP3(filepath)
                length += audio.info.length * 1000
                map.append(audio.info.length * 1000)

        return length, map

    def get_thread_suitable_pauses_lenght(thread, duration):
        audios_lenght ,_ = TextToSpeech.get_thread_audios_lenght(thread)
        time_for_pauses = (duration * 1000) - audios_lenght
        return (time_for_pauses / (len(thread.comments) + 1 + 1 + 1))

    def make_full_thread_audio(thread, duration):
        filepath = f"storage/audio/threads/full/{duration}/{thread.identifier}.mp3"
        pause_lenght = TextToSpeech.get_thread_suitable_pauses_lenght(thread, duration)
        mp3_files = [f"storage/audio/threads/{thread.identifier}.mp3"]
        for comment in thread.comments:
            mp3_files.append(f"storage/audio/comments/{comment.identifier}.mp3")

        AudioSegment.ffmpeg = which("ffmpeg")
        combined_audio = AudioSegment.empty()
        for mp3_file in mp3_files:
            absolute_path = os.path.abspath(mp3_file)
            if not os.path.exists(absolute_path):
                print(f"File not found: {absolute_path}")
                return False
            combined_audio += AudioSegment.silent(duration=pause_lenght)
            combined_audio += AudioSegment.from_mp3(absolute_path)

        combined_audio += AudioSegment.silent(duration=pause_lenght)

        make_dir(filepath)
        combined_audio.export(filepath, format="mp3")

        print(f"Combined MP3 saved at {filepath}")

    def get_thread_timing(thread):
        pause = TextToSpeech.get_thread_suitable_pauses_lenght(thread)
        _, threadMap = TextToSpeech.get_thread_audios_lenght(thread)

        threadTimings = (pause,)

        for point in threadMap:
            threadTimings += (point,)
            threadTimings += (pause,)

        return threadTimings

    def adjust_comments_by_duration(thread, duration):
        suitable_pauses = TextToSpeech.get_thread_suitable_pauses_lenght(thread, duration)
        print(f"{int(suitable_pauses)}")
        if suitable_pauses > max_pause:
            return "+"

        if suitable_pauses < min_pause:
            return "-"

        return True

class Elevenlabs:
    def __init__(self):
        self.client = ElevenLabs(
            api_key=elevenlabs_config["api_key"],
        )

    def get_remaining(self):
        subscription = self.client.user.get_subscription()
        return int(subscription.character_limit) - int(subscription.character_count)

    def check_remaining_by_text(self, text):
        if len(text) > self.get_remaining():
            print("Elevenlabs empty")
            exit()

    def generate(self, text, filepath, voice_id = 'pNInz6obpgDQGcFmaJgB'):
        self.check_remaining_by_text(text)
        audio = self.client.generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
        )

        save(audio, filepath)

        print(f"{filepath} saved successfully!")
