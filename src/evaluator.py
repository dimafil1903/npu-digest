"""Quality evaluator — uses LLM to score its own output."""
import re
import requests
from .config import RkllamaConfig

EVAL_SYSTEM = (
    "Ти суворий редактор технічного дайджесту. "
    "Оцінюй об'єктивно, без поблажок."
)

EVAL_PROMPT = """Оціни якість цього summary. Будь ЛІБЕРАЛЬНИМ — якщо summary містить конкретну інформацію, ставь 6+.

Заголовок: {title}
Summary:
{summary}

Критерії (0-2 бали кожен):
1. Конкретність: є хоча б 1-2 факти/цифри/назви (не лише загальні фрази) → 2
2. Мова: переважно українська, без грубих помилок → 2
3. Релевантність: хоч якось стосується tech/backend/security/AI → 2
4. Формат: 3 bullet points з emoji, до 150 слів → 2

SCORE 6+ = прийнятна якість, не треба retry.
SCORE 4-5 = є проблеми але терпимо.
SCORE 0-3 = треба переробити.

Відповідай ТІЛЬКИ:
SCORE: X/8
ПРИЧИНА: одне речення (або "все добре")"""


def evaluate(title: str, summary: str, cfg: RkllamaConfig) -> tuple[int, str]:
    """Returns (score 0-8, reason)."""
    if summary.startswith("⏭"):
        return 8, "відфільтровано коректно"

    prompt = EVAL_PROMPT.format(title=title, summary=summary)
    try:
        resp = requests.post(
            f"{cfg.url}/v1/chat/completions",
            json={
                "model": cfg.model,
                "messages": [
                    {"role": "system", "content": EVAL_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "max_tokens": 80,
                "temperature": 0.3,
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()

        # Parse score
        match = re.search(r"SCORE:\s*(\d+)/8", text)
        score = int(match.group(1)) if match else 4

        reason_match = re.search(r"ПРИЧИНА:\s*(.+)", text)
        reason = reason_match.group(1).strip() if reason_match else text

        return score, reason
    except Exception as e:
        return 4, f"eval error: {e}"
