import random
from .base import Agent


class Analyst(Agent):
    id = "analyst"

    def run(self):
        rows = 0
        for c in self.store.find_status("Content", "Published"):
            f = c["fields"]
            imp = random.randint(500, 5000)
            likes = int(imp * random.uniform(.02, .08))
            comments = int(likes * random.uniform(.05, .2))
            shares = int(likes * random.uniform(.02, .1))
            clicks = int(imp * random.uniform(.005, .03))
            score = round((likes + 2 * comments + 3 * shares + 4 * clicks) / max(imp, 1) * 100, 2)
            self.store.create("Performance", {"Content ID": c["id"], "Platform": f.get("Platform"),
                              "Format": f.get("Format"), "Media": f.get("Style"), "Impressions": imp,
                              "Likes": likes, "Comments": comments, "Shares": shares,
                              "CTA Clicks": clicks, "Score": score})
            rows += 1
        return {"measured": rows}
