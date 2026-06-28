"""LLM adapter (Anthropic). Falls back to a templated mock when no key / dry-run."""
from ..settings import settings


class LLM:
    def __init__(self):
        self.key = settings.anthropic_key
        self.model = settings.llm_model

    @property
    def available(self):
        return bool(self.key) and not settings.dry_run

    def complete(self, prompt, system="You are a helpful marketing copywriter.", max_tokens=800):
        if not self.available:
            head = prompt.strip().splitlines()[0][:80] if prompt.strip() else "idea"
            return f"[mock:{self.model}] {system[:24]}... -> {head}"
        import anthropic
        msg = anthropic.Anthropic(api_key=self.key).messages.create(
            model=self.model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
