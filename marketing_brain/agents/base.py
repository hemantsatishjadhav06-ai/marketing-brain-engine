import logging
from ..providers import LLM


class Agent:
    id = "agent"

    def __init__(self, ctx):
        self.ctx = ctx
        self.store = ctx["store"]
        self.budget = ctx["budget"]
        self.settings = ctx["settings"]
        self.brand = self.settings.brand
        self.log = logging.getLogger(self.id)
        self.llm = LLM()

    def run(self):
        return {}
