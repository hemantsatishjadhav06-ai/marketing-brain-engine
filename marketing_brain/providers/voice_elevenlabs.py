"""Voiceover / audio (ElevenLabs)."""
from .base import MediaProvider


class VoiceProvider(MediaProvider):
    PID = "voice_elevenlabs"; COST = 0.05; KIND = "audio"

    def _live(self, prompt, voice="Rachel", **kw):
        # TODO: ElevenLabs TTS -> upload -> return URL.
        raise NotImplementedError("Add ElevenLabs call here")
