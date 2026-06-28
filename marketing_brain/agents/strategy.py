import random
from .base import Agent


class Strategist(Agent):
    id = "strategist"
    FORMATS = ["Cheatsheet", "Carousel", "Thought Leadership", "Q&A Video", "Quote", "Case Study"]
    STYLES = ["Text", "Text & Image", "Post", "Video", "AI Avatar"]

    def run(self):
        platforms = self.brand.get("platforms", ["Instagram"])
        n = 0
        for idea in self.store.find_status("Ideas", "Shortlisted"):
            f = idea["fields"]
            plat = f.get("Source") if f.get("Source") in platforms else random.choice(platforms)
            self.store.create("Content", {
                "Topic": f.get("Topic"), "Perspective": f.get("Angle"),
                "Platform": plat, "Style": random.choice(self.STYLES),
                "Format": random.choice(self.FORMATS), "Status": "Draft", "Owner": "marketing-brain"})
            self.store.update("Ideas", idea["id"], {"Status": "Used"})
            n += 1
        return {"briefed": n}
