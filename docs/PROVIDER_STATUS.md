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
