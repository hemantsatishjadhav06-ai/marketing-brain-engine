"""Short-form / b-roll video (Higgsfield, Kling, Runway...)."""
from .base import MediaProvider


class ShortVideoProvider(MediaProvider):
    PID = "video_shortform"; COST = 0.40; KIND = "short_video"

    def _live(self, prompt, duration=15, **kw):
        # TODO: text/image -> video; poll; return URL.
        raise NotImplementedError("Add short-form video call here")
