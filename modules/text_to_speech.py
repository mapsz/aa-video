from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
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

        filepath = f"storage/audio/threads/{thread.identifier}"
        if not os.path.exists(filepath):
            make_dir(filepath)
            elevenlabs.generate(thread.title, filepath)

        for comment in thread.comments:
            filepath = f"storage/audio/comments/{comment.identifier}"
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

    def get_thread_suitable_pauses_lenght(thread):
        audios_lenght ,_ = TextToSpeech.get_thread_audios_lenght(thread)
        time_for_pauses = 60000 - audios_lenght
        return (time_for_pauses / (len(thread.comments) + 1 + 1 + 1))

    def make_full_thread_audio(thread, pause_lenght = 1000):
        print(pause_lenght)
        mp3_files = [f"storage/audio/threads/{thread.identifier}.mp3"]
        for comment in thread.comments:
            mp3_files.append(f"storage/audio/comments/{comment.identifier}.mp3")

        print(len(mp3_files))

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

        print(combined_audio)

        filepath = f"storage/audio/threads/full/{thread.identifier}.mp3"
        make_dir(filepath)
        combined_audio.export(filepath, format="mp3")

        print(f"Combined MP3 saved at {filepath}")
        return True

    def get_thread_timing(thread):
        pause = TextToSpeech.get_thread_suitable_pauses_lenght(thread)
        _, threadMap = TextToSpeech.get_thread_audios_lenght(thread)

        threadTimings = (pause,)

        for point in threadMap:
            threadTimings += (point,)
            threadTimings += (pause,)

        return threadTimings

class Elevenlabs:
    def __init__(self):
        self.client = ElevenLabs(
            api_key=elevenlabs_config["api_key"],
        )

    def generate(self, text, filepath, voice_id = 'pNInz6obpgDQGcFmaJgB'):
        audio = self.client.generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
        )

        save(audio, filepath + ".mp3")

        print(f"{filepath}.mp3 saved successfully!")
