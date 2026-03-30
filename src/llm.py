"""rkllama OpenAI-compatible client."""
import requests
from typing import Optional
from .config import RkllamaConfig


SYSTEM_PROMPT = "Ти асистент для senior backend розробника. Завжди відповідай ТІЛЬКИ українською мовою."

SUMMARIZE_PROMPT = """Стаття: {title}
Джерело: {source}

Текст:
{text}

---
Зроби 3 bullet points українською (без ** або ##, тільки текст і emoji).
Що важливо для backend розробника (Go, Python, AI/ML). До 100 слів."""


def summarize(
    title: str,
    source: str,
    text: str,
    cfg: RkllamaConfig,
) -> Optional[str]:
    """Send text to rkllama and get Ukrainian summary."""
    prompt = SUMMARIZE_PROMPT.format(title=title, source=source, text=text[:4000])

    try:
        resp = requests.post(
            f"{cfg.url}/v1/chat/completions",
            json={
                "model": cfg.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "max_tokens": cfg.max_tokens,
                "temperature": cfg.temperature,
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"    LLM error: {e}")
        return None
