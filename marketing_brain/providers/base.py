"""Shared media-provider base. Subclasses set PID, COST and implement _live()."""
import hashlib
from ..settings import settings


class MediaProvider:
    PID = "base"
    COST = 0.0
    KIND = "asset"

    def __init__(self):
        self.key = settings.provider_keys.get(self.PID, "")

    @property
    def available(self):
        return bool(self.key) and not settings.dry_run

    def _slug(self, text):
        return hashlib.sha1((text or "").encode()).hexdigest()[:10]

    def _mock(self, prompt):
        return {"provider": self.PID, "kind": self.KIND, "mock": True, "cost": 0.0,
                "url": f"https://mock.local/{self.PID}/{self._slug(prompt)}.out",
                "prompt": prompt}

    def _live(self, prompt, **kw):
        raise NotImplementedError

    def generate(self, prompt, **kw):
        if not self.available:
            return self._mock(prompt)
        out = self._live(prompt, **kw)
        out.setdefault("cost", self.COST)
        out.setdefault("provider", self.PID)
        out["mock"] = False
        return out
