"""rkllama OpenAI-compatible client."""
import requests
from typing import Optional
from .config import RkllamaConfig


SYSTEM_PROMPT = (
    "Ти технічний редактор для senior backend розробника (Go, Python, AI/ML). "
    "Завжди відповідай ТІЛЬКИ українською мовою. "
    "Пиши конкретно: назви технологій, цифри, практичні висновки. "
    "Ніколи не пиши загальні фрази типу 'важливо зрозуміти' або 'необхідно перевіряти'."
)

SUMMARIZE_PROMPT = """Стаття: {title}
Джерело: {source}

Текст:
{text}

---
Дай 3 конкретні bullet points українською. Формат кожного:
emoji + конкретний факт або висновок (що саме, яка цифра, яка технологія, який практичний вплив).

Якщо стаття взагалі не стосується технологій, безпеки, AI, хмари, інструментів розробника — напиши одним рядком: "⏭ Нерелевантно"
Якщо стаття технічна або про індустрію — зроби bullet points.

ВАЖЛИВО: відповідай ВИКЛЮЧНО українською мовою. Без markdown ** або ##. До 120 слів."""


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
