from .base import Agent
from ..providers import get_provider

VIDEO_STYLES = ("Video", "AI Avatar", "Vishnu Avatar")


class Copywriter(Agent):
    id = "copywriter"

    def run(self):
        n = 0
        for c in self.store.find_status("Content", "Draft"):
            f = c["fields"]
            sysmsg = (f"Brand voice: {self.brand.get('tone')}. "
                      f"Avoid: {', '.join(self.brand.get('forbidden_words', []))}.")
            hook = self.llm.complete(f"Write a scroll-stopping hook for: {f.get('Topic')}",
                                     system=sysmsg, max_tokens=60)
            cap = self.llm.complete(
                f"Write a {f.get('Platform')} caption for: {f.get('Topic')} ({f.get('Perspective')})",
                system=sysmsg)
            self.store.update("Content", c["id"], {
                "Hook": hook, "Caption": cap, "CTA": "Learn more",
                "Hashtags": " ".join(self.brand.get("hashtag_bank", [])), "Status": "Generating"})
            n += 1
        return {"written": n}


class Designer(Agent):
    id = "designer"

    def run(self):
        img, canva = get_provider("image_flux"), get_provider("design_canva")
        n = 0
        for c in self.store.find_status("Content", "Generating"):
            f = c["fields"]
            prompt = f.get("Image Prompt") or f"{f.get('Topic')} - {self.brand.get('niche')}, clean photography"
            a = img.generate(prompt, ratio="4:5")
            self.budget.charge(a.get("cost", 0), "image")
            self.store.update("Content", c["id"], {"Image Prompt": prompt})
            self.store.create("Assets", {"Content ID": c["id"], "Type": "image",
                              "Provider": a["provider"], "URL": a["url"], "Prompt": prompt, "Status": "Ready"})
            if (f.get("Format") or "").lower().find("carousel") >= 0 or f.get("Style") == "Post":
                ca = canva.generate(f.get("Topic", ""))
                self.store.create("Assets", {"Content ID": c["id"], "Type": "carousel",
                                  "Provider": ca["provider"], "URL": ca["url"], "Status": "Ready"})
            n += 1
        return {"images": n}


class VideoProducer(Agent):
    id = "video_producer"

    def run(self):
        short, avatar = get_provider("video_shortform"), get_provider("video_heygen")
        n = 0
        for c in self.store.find_status("Content", "Generating"):
            style = c["fields"].get("Style") or ""
            if style not in VIDEO_STYLES:
                continue
            topic = c["fields"].get("Topic", "")
            prov = avatar if "Avatar" in style else short
            script = self.llm.complete(f"Write a 20s short-form video script: {topic}")
            v = prov.generate(topic, duration=20)
            self.budget.charge(v.get("cost", 0), "video")
            self.store.update("Content", c["id"], {"Script": script})
            self.store.create("Assets", {"Content ID": c["id"], "Type": v.get("kind", "video"),
                              "Provider": v["provider"], "URL": v["url"], "Status": "Ready"})
            n += 1
        return {"videos": n}


class VoiceArtist(Agent):
    id = "voice_artist"

    def run(self):
        voice = get_provider("voice_elevenlabs")
        n = 0
        for c in self.store.find_status("Content", "Generating"):
            if (c["fields"].get("Style") or "") not in VIDEO_STYLES:
                continue
            a = voice.generate(c["fields"].get("Script") or c["fields"].get("Topic", ""))
            self.budget.charge(a.get("cost", 0), "voice")
            self.store.create("Assets", {"Content ID": c["id"], "Type": "audio",
                              "Provider": a["provider"], "URL": a["url"], "Status": "Ready"})
            n += 1
        return {"voiceovers": n}


class Editor(Agent):
    id = "editor"

    def run(self):
        n = 0
        for c in self.store.find_status("Content", "Generating"):
            assets = self.store.list("Assets", {"Content ID": c["id"]})
            urls = "; ".join(a["fields"].get("URL", "") for a in assets)
            self.store.update("Content", c["id"], {"Asset URLs": urls, "Status": "Needs Review"})
            n += 1
        return {"assembled": n}


class BrandGuardian(Agent):
    id = "brand_guardian"

    def run(self):
        banned = [w.lower() for w in self.brand.get("forbidden_words", [])]
        flagged = 0
        for c in self.store.find_status("Content", "Needs Review"):
            text = " ".join(str(c["fields"].get(k, "")) for k in ("Hook", "Caption", "CTA")).lower()
            if any(b and b in text for b in banned):
                self.store.update("Content", c["id"], {"Status": "Rejected", "Notes": "Brand: forbidden word"})
                flagged += 1
        awaiting = len(self.store.find_status("Content", "Needs Review"))
        return {"rejected": flagged, "awaiting_human_approval": awaiting}
