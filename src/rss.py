"""RSS feed fetching."""
import feedparser
from dataclasses import dataclass
from typing import List
from .config import FeedConfig


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source: str


def fetch_feed(feed_cfg: FeedConfig) -> List[Article]:
    """Fetch articles from a single RSS feed."""
    parsed = feedparser.parse(feed_cfg.url)
    articles = []

    for entry in parsed.entries[: feed_cfg.max_items]:
        articles.append(Article(
            title=entry.get("title", ""),
            url=entry.get("link", ""),
            summary=entry.get("summary", ""),
            source=feed_cfg.name,
        ))

    return articles


def fetch_all(feeds: List[FeedConfig]) -> List[Article]:
    """Fetch articles from all configured feeds."""
    all_articles = []
    for feed in feeds:
        try:
            articles = fetch_feed(feed)
            all_articles.extend(articles)
            print(f"  [{feed.name}] {len(articles)} articles")
        except Exception as e:
            print(f"  [{feed.name}] error: {e}")
    return all_articles
