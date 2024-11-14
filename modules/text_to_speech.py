from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from config import elevenlabs_config

class Elevenlabs:
    def __init__(self):
        self.client = ElevenLabs(
            api_key=elevenlabs_config["api_key"],
        )

    def generate(self, text):
        audio = self.client.generate(
            text=text,
            voice=Voice(
                voice_id='nPczCjzI2devNBz1zQrb',
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
        )

        save(audio, "111.mp3")

        print("Audio saved successfully!")