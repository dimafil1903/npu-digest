"""Fetch and clean article text."""
import requests
from bs4 import BeautifulSoup
from .rss import Article


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; npu-digest/1.0)"}
TIMEOUT = 10


def fetch_text(article: Article, max_words: int = 3000) -> str:
    """Fetch full article text, strip HTML, truncate."""
    if not article.url:
        return article.summary

    try:
        resp = requests.get(article.url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try to find main content
        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=lambda c: c and "content" in c.lower())
            or soup.body
        )

        text = (main or soup).get_text(separator=" ", strip=True)
        words = text.split()
        return " ".join(words[:max_words])

    except Exception:
        # Fall back to RSS summary
        return article.summary
