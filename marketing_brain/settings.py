"""Central config: env + YAML. Import `settings` everywhere."""
import os, json, pathlib
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
try:
    import yaml
except Exception:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"


def _yaml(name, default):
    p = CONFIG / name
    if yaml and p.exists():
        return yaml.safe_load(p.read_text())
    return default


class Settings:
    # control plane
    airtable_key = os.getenv("AIRTABLE_API_KEY", "")
    airtable_base = os.getenv("AIRTABLE_BASE_ID", "")
    sheet_id = os.getenv("SHEET_ID", "")
    google_sa = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    # llm
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    # providers
    provider_keys = {
        "image_flux": os.getenv("FLUX_API_KEY", "") or os.getenv("HIGGSFIELD_API_KEY", ""),
        "design_canva": os.getenv("CANVA_API_KEY", ""),
        "video_heygen": os.getenv("HEYGEN_API_KEY", ""),
        "video_shortform": os.getenv("HIGGSFIELD_API_KEY", ""),
        "voice_elevenlabs": os.getenv("ELEVENLABS_API_KEY", ""),
    }
    # guardrails
    daily_budget = float(os.getenv("DAILY_USD_BUDGET", "5") or 5)
    dry_run = os.getenv("DRY_RUN", "true").lower() in ("1", "true", "yes")
    # yaml
    brand = _yaml("brand.yaml", {"brand_name": "Your Brand", "tone": "friendly expert",
                                 "forbidden_words": [], "platforms": ["Instagram"]})
    agents = _yaml("agents.yaml", {"team": []})
    providers = _yaml("providers.yaml", {})

    @property
    def control_plane(self):
        if self.airtable_key and self.airtable_base:
            return "airtable"
        if self.google_sa and self.sheet_id:
            return "sheets"
        return "local"


settings = Settings()
