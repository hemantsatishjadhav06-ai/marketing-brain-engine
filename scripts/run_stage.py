"""CLI: python -m scripts.run_stage <discover|strategy|create|schedule|publish|engage|analyze|all>"""
import sys, json, logging
from marketing_brain.orchestrator import Orchestrator, ALL_ORDER


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    orch = Orchestrator()
    if stage == "all":
        out = orch.run_all()
    elif stage in ALL_ORDER:
        out = {stage: orch.run_stage(stage)}
    else:
        print("stages:", ", ".join(ALL_ORDER + ["all"])); sys.exit(2)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
