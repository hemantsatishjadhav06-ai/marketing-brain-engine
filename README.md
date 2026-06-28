# marketing-brain

An autonomous, human-approved content engine. A lean **orchestrator** drives a team of
specialist **agents** that discover ideas, generate copy + media (image, carousel,
avatar video, short-form video, voice), schedule, and (after a human approves) publish —
then learn from performance.

- **Compute:** GitHub Actions (serverless cron + manual dispatch). No server to host.
- **Control plane / UI / memory:** Airtable (default) or Google Sheets. Swappable.
- **Approval:** Nothing publishes until a human flips a record to `Approved`.
- **Runs with zero API keys** in *mock mode*, so CI is always green.

```
Idea  →  Strategy  →  Create (copy+media)  →  [HUMAN APPROVES]  →  Schedule  →  Publish  →  Engage  →  Analyze ↺
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in keys when ready (optional)
make smoke                      # runs the full pipeline in mock mode
python -m scripts.run_stage discover
python -m scripts.run_stage create
# ...flip a record to Approved in Airtable/Sheet...
python -m scripts.run_stage publish
```

With no credentials set, data is stored locally in `data/local_store.json` so you can
see the whole loop work before wiring any provider.

## Configure the control plane

| Mode | Env vars |
|------|----------|
| Airtable | `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID` |
| Google Sheets | `GOOGLE_SERVICE_ACCOUNT_JSON`, `SHEET_ID` |
| Local (default) | none — writes `data/local_store.json` |

Provision the Airtable tables once: `python -m scripts.setup_airtable`

## The agent team

See `config/agents.yaml` and `docs/ARCHITECTURE.md`. Thirteen specialists + one
orchestrator, each dormant until its stage fires.

## Security

Secrets live in **GitHub Actions Secrets** / your local `.env` — never in code.
See `docs/ARCHITECTURE.md` → Security. If you ever paste a token anywhere public,
rotate it immediately at https://github.com/settings/tokens .

## License

MIT — see `LICENSE`.
