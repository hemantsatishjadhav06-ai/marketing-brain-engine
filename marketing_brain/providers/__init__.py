"""Provider adapters. Each runs live when its API key is set, else returns a deterministic
mock so the whole engine works end-to-end with zero credentials."""
from .llm_anthropic import LLM
from .image_flux import ImageProvider
from .design_canva import DesignProvider
from .video_heygen import AvatarVideoProvider
from .video_shortform import ShortVideoProvider
from .voice_elevenlabs import VoiceProvider

REGISTRY = {
    "image_flux": ImageProvider,
    "design_canva": DesignProvider,
    "video_heygen": AvatarVideoProvider,
    "video_shortform": ShortVideoProvider,
    "voice_elevenlabs": VoiceProvider,
}


def get_provider(pid):
    return REGISTRY[pid]()
