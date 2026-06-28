"""The Conductor: runs a stage by invoking its agents in order."""
import logging
from .settings import settings
from .budget import Budget
from .control_plane import get_store
from . import agents as A

log = logging.getLogger("orchestrator")

STAGES = {
    "discover": [A.TrendScout, A.IdeaMiner, A.SeoAnalyst],
    "strategy": [A.Strategist],
    "create":   [A.Copywriter, A.Designer, A.VideoProducer, A.VoiceArtist, A.Editor, A.BrandGuardian],
    "schedule": [A.Scheduler],
    "publish":  [A.Publisher],
    "engage":   [A.CommunityManager],
    "analyze":  [A.Analyst],
}
ALL_ORDER = ["discover", "strategy", "create", "schedule", "publish", "engage", "analyze"]


class Orchestrator:
    def __init__(self):
        self.store = get_store()
        self.budget = Budget()
        log.info("control plane: %s | dry_run=%s | budget=$%.2f",
                 settings.control_plane, settings.dry_run, self.budget.limit)

    def run_stage(self, stage):
        agents = STAGES[stage]
        ctx = {"store": self.store, "budget": self.budget, "settings": settings, "stage": stage}
        results = []
        for cls in agents:
            agent = cls(ctx)
            log.info("-> %s", agent.id)
            results.append({"agent": agent.id, "output": agent.run()})
        return results

    def run_all(self):
        return {s: self.run_stage(s) for s in ALL_ORDER}
