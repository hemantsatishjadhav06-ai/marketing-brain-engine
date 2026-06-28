"""Tiny daily-spend guardrail. Persisted in the control plane Jobs table cost sums."""
from .settings import settings


class BudgetError(RuntimeError):
    pass


class Budget:
    def __init__(self, limit=None):
        self.limit = float(limit if limit is not None else settings.daily_budget)
        self.spent = 0.0

    def charge(self, usd, what=""):
        if self.spent + usd > self.limit:
            raise BudgetError(f"Daily budget ${self.limit:.2f} exceeded by '{what}' (+${usd:.2f})")
        self.spent += usd
        return self.spent
