import datetime, random
from .base import Agent

SLOTS = ["09:00", "13:00", "17:00", "21:00"]


class Scheduler(Agent):
    id = "scheduler"

    def run(self):
        n = 0
        for c in self.store.find_status("Content", "Approved"):
            date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
            self.store.create("Calendar", {"Content ID": c["id"], "Platform": c["fields"].get("Platform"),
                              "Publish Date": date, "Slot": random.choice(SLOTS), "Status": "Scheduled"})
            self.store.update("Content", c["id"], {"Status": "Scheduled", "Publish Date": date})
            n += 1
        return {"scheduled": n}


class Publisher(Agent):
    id = "publisher"

    def run(self):
        # HARD GATE: by the time we are here a human has Approved and the Scheduler moved
        # the record to Scheduled. Bots can never self-approve (see state.py).
        published = 0
        for c in self.store.find_status("Content", "Scheduled"):
            # TODO: call the real platform API. Mock: mark Published.
            self.store.update("Content", c["id"], {"Status": "Published"})
            published += 1
        return {"published": published}
