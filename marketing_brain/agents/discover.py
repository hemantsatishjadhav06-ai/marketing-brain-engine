from .base import Agent


class TrendScout(Agent):
    id = "trend_scout"

    def run(self):
        niche = self.brand.get("niche", "your niche")
        seeds = [
            (f"Why {niche} pros obsess over the small details", "educational", "X", 87),
            (f"3 myths about {niche} everyone repeats", "myth-busting", "LinkedIn", 74),
            (f"Behind the scenes of {niche}", "behind-the-scenes", "Instagram", 65),
        ]
        for topic, angle, src, score in seeds:
            self.store.create("Ideas", {"Topic": topic, "Angle": angle, "Source": src,
                                        "Signal Score": score, "Status": "New"})
        return {"created": len(seeds)}


class IdeaMiner(Agent):
    id = "idea_miner"

    def run(self):
        seen, kept = set(), 0
        for r in self.store.find_status("Ideas", "New"):
            t = r["fields"].get("Topic", "")
            if t in seen:
                continue
            seen.add(t)
            self.store.update("Ideas", r["id"], {"Status": "Shortlisted"})
            kept += 1
        return {"shortlisted": kept}


class SeoAnalyst(Agent):
    id = "seo_analyst"

    def run(self):
        n = 0
        for r in self.store.find_status("Ideas", "Shortlisted"):
            f = r["fields"]
            if f.get("Keyword"):
                continue
            kw = " ".join(f.get("Topic", "").lower().split(" ")[:4])
            self.store.update("Ideas", r["id"], {"Keyword": kw,
                              "Cluster": self.brand.get("niche", "general"), "Intent": "Informational"})
            n += 1
        return {"tagged": n}
