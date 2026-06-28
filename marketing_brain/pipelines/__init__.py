"""Thin stage entry points (wrap the Orchestrator)."""
from ..orchestrator import Orchestrator, ALL_ORDER


def run(stage):
    return Orchestrator().run_stage(stage)


def run_all():
    return Orchestrator().run_all()
