> **Update (2026-09-06).** The five per-stage cron workflows described below as
> "green and inert" have been **removed**. They advanced no records because their
> state (`data/local_store.json`) died with each GitHub-runner. The real content
> pipeline lives in the sibling **marketing-brain** app on Railway, which produces
> the creatives (verified live). A single `heartbeat` workflow now drives that app
> via its `/api/cron` endpoint instead of running these stub stages locally. The
> analysis below is kept for the record — it is the *why* behind that change.

# Provider status — what is actually wired

Verified by running the full pipeline on this repo (`make smoke`, `make test`, and a
direct provider call). Keep this table honest: it is the difference between "we set the
key" and "we get an asset".

| Provider adapter | Env var | `_live()` implemented? | What happens today |
|---|---|---|---|
| `llm_anthropic` | `ANTHROPIC_API_KEY` | yes | real copy when the key is set |
| `image_flux` | `FLUX_API_KEY` / `HIGGSFIELD_API_KEY` | **no — raises `NotImplementedError`** | mock URL only |
| `design_canva` | `CANVA_API_KEY` | **no** | mock URL only |
| `video_heygen` | `HEYGEN_API_KEY` | **no** | mock URL only |
| `video_shortform` | `HIGGSFIELD_API_KEY` | **no** | mock URL only |
| `voice_elevenlabs` | `ELEVENLABS_API_KEY` | **no** | mock URL only |

## There is no fal.ai adapter in this repo

`FAL_KEY` is not read anywhere in `marketing_brain/`. Setting it here changes nothing.
fal.ai rendering lives in the sibling repo `marketing-brain`
(`app/ai/brain.py` → `fal_image` / `fal_video` / `fal_voice`), which is where the
Neopolis creatives are actually produced.

## How the two failure modes look

`MediaProvider.available` is `bool(key) and not settings.dry_run`, so:

- **`DRY_RUN=true` (default, and what CI runs)** — the key is ignored and every asset is a
  placeholder pointing at a host that does not exist:

  ```python
  {'provider': 'image_flux', 'kind': 'image', 'mock': True, 'cost': 0.0,
   'url': 'https://mock.local/image_flux/13708352ba.out', ...}
  ```

- **`DRY_RUN=false` with a key set** — the adapter is reached and raises:

  ```
  NotImplementedError: Add Flux/Higgsfield call here
  ```

So a media key on this repo either does nothing (mock) or crashes the Designer /
Video Producer / Voice Artist agents (live). Wire `_live()` before flipping `DRY_RUN`.

## Reproducing

```bash
python - <<'PY'
import os
os.environ["FLUX_API_KEY"] = "demo-key"; os.environ["DRY_RUN"] = "false"
from marketing_brain.providers import get_provider
get_provider("image_flux").generate("test prompt", ratio="4:5")
PY
```

---

# The scheduled workflows are green and inert

Separate from the provider stubs, and more consequential: the cron workflows have
run **989 times** and produced nothing. Every run succeeds, so nothing signals it.

Two consecutive scheduled runs on `main`, straight from the job logs:

```
discover  2026-08-16T06:29:28   trend_scout created: 3   idea_miner shortlisted: 3   seo_analyst tagged: 3
create    2026-08-17T01:12:48   copywriter written: 0    designer images: 0    video_producer videos: 0
                                voice_artist voiceovers: 0    editor assembled: 0
                                brand_guardian rejected: 0, awaiting_human_approval: 0
```

`discover` mines 3 ideas; `create` then finds zero rows to work on. The `create`
step completes in **1 second** — no LLM call is ever made.

## Why

`settings.control_plane` picks Airtable only when `AIRTABLE_API_KEY` **and**
`AIRTABLE_BASE_ID` are both set. Without the secret it falls back to the local
store — `data/local_store.json` — which lives on the GitHub Actions runner. The
runner is destroyed when the job ends, taking the ideas with it. The next stage
starts from an empty store on a fresh runner.

So the pipeline is not a loop. Each stage is an isolated run against a blank slate,
and the human-approval gate at the centre of the design never receives a row.

## Fix

Set the `AIRTABLE_API_KEY` repository secret (`AIRTABLE_BASE_ID` is already
`appvpMfpbNQDkUGeF` in `.env.example`), then run `python -m scripts.setup_airtable`
once to provision the tables. Until state persists between runs, wiring the media
providers above changes nothing — there is never a row for them to act on.
