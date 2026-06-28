from .base import Agent


class CommunityManager(Agent):
    id = "community_manager"

    def run(self):
        drafted = 0
        for c in self.store.find_status("Content", "Published"):
            txt = self.llm.complete(f"Draft a friendly first comment to pin under: {c['fields'].get('Topic')}")
            self.store.create("Engagements", {"Content ID": c["id"], "Type": "first_comment",
                              "Draft": txt, "Status": "Draft"})
            drafted += 1
        return {"drafted": drafted}
