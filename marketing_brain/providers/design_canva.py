"""Carousel / templated design (Canva). Use a brand template + autofill API."""
from .base import MediaProvider


class DesignProvider(MediaProvider):
    PID = "design_canva"; COST = 0.0; KIND = "carousel"

    def _live(self, prompt, template_id=None, slides=None, **kw):
        # TODO: Canva Autofill API -> export -> return URL.
        raise NotImplementedError("Add Canva autofill call here")
