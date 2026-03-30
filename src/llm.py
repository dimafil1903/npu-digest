"""rkllama OpenAI-compatible client with self-evaluation loop."""
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

RETRY_PROMPT = """Стаття: {title}

Попередня спроба summary була погана: {reason}

Текст:
{text}

---
Спробуй ще раз. Будь КОНКРЕТНИМ: тільки факти, цифри, назви технологій.
Без загальних фраз. ТІЛЬКИ українська мова. 3 bullet points з emoji."""


def _call(messages: list, cfg: RkllamaConfig, max_tokens: int = 300) -> Optional[str]:
    try:
        resp = requests.post(
            f"{cfg.url}/v1/chat/completions",
            json={
                "model": cfg.model,
                "messages": messages,
                "stream": False,
                "max_tokens": max_tokens,
                "temperature": cfg.temperature,
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"    LLM error: {e}")
        return None


def summarize(
    title: str,
    source: str,
    text: str,
    cfg: RkllamaConfig,
    max_retries: int = 2,
    min_score: int = 5,
) -> Optional[str]:
    """Summarize with self-evaluation retry loop."""
    import re
    from .evaluator import evaluate

    prompt = SUMMARIZE_PROMPT.format(title=title, source=source, text=text[:4000])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    best_result = None
    best_score = 0

    for attempt in range(1, max_retries + 2):
        result = _call(messages, cfg)
        if not result:
            return None

        # Strip any markdown that snuck in
        result = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", result)
        result = re.sub(r"#{1,3}\s*", "", result)

        # Skip evaluation for filtered articles
        if result.startswith("⏭"):
            return result

        score, reason = evaluate(title, result, cfg)
        print(f"    attempt {attempt}: score {score}/8 — {reason}")

        if score > best_score:
            best_score = score
            best_result = result

        if score >= min_score:
            return result

        if attempt <= max_retries:
            retry_prompt = RETRY_PROMPT.format(
                title=title, reason=reason, text=text[:4000]
            )
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": retry_prompt},
            ]
            print(f"    retrying...")

    print(f"    best score was {best_score}/8")
    return best_result  # return best attempt
