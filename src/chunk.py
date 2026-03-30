"""Split text into chunks for LLM context window."""
from typing import List


def chunk_text(text: str, max_words: int = 1500) -> List[str]:
    """Split text into chunks of max_words words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i : i + max_words]))
    return chunks or [""]
