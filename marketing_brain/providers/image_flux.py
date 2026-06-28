"""Image generation (Flux / Higgsfield). Wire _live() to your endpoint when ready."""
from .base import MediaProvider


class ImageProvider(MediaProvider):
    PID = "image_flux"; COST = 0.03; KIND = "image"

    def _live(self, prompt, ratio="1:1", **kw):
        # TODO: POST prompt to Flux/Higgsfield; poll; return hosted URL.
        raise NotImplementedError("Add Flux/Higgsfield call here")
