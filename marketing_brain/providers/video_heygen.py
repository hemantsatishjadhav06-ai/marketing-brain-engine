"""Avatar / talking-head video (HeyGen)."""
from .base import MediaProvider


class AvatarVideoProvider(MediaProvider):
    PID = "video_heygen"; COST = 0.50; KIND = "avatar_video"

    def _live(self, prompt, avatar_id=None, voice_id=None, **kw):
        # TODO: HeyGen v2/video/generate -> poll status -> return URL.
        raise NotImplementedError("Add HeyGen call here")
