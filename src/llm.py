"""rkllama OpenAI-compatible client."""
import requests
from typing import Optional
from .config import RkllamaConfig


SUMMARIZE_PROMPT = """Article title: {title}
Source: {source}

Text:
{text}

---
Summarize in 3 bullet points (Ukrainian), focus on what's important for a senior backend developer (Go, Python, AI/ML).
No markdown symbols like ** or ##, just plain text with emoji bullets.
Be concise, max 100 words total."""


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
                "messages": [{"role": "user", "content": prompt}],
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
