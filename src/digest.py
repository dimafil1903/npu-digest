"""Main digest pipeline."""
import time
from .config import load_config
from .rss import fetch_all
from .fetch import fetch_text
from .llm import summarize
from .telegram import send


def run(config_path: str = "config.yaml") -> None:
    cfg = load_config(config_path)

    print("Fetching RSS feeds...")
    articles = fetch_all(cfg.feeds)
    print(f"Total: {len(articles)} articles\n")

    summaries = []
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] {article.title[:60]}")

        text = fetch_text(article, cfg.digest.max_article_words)
        print(f"  fetched {len(text.split())} words")

        summary = summarize(article.title, article.source, text, cfg.rkllama)
        if summary:
            summaries.append(f"📰 {article.title}\n{summary}\n🔗 {article.url}")
            print(f"  summarized")
        else:
            print(f"  skipped (no summary)")

    if not summaries:
        print("No summaries generated.")
        return

    date_str = time.strftime("%d.%m.%Y %H:%M")
    header = f"🤖 IT дайджест {date_str} (NPU)\n{'─'*30}\n\n"
    message = header + "\n\n".join(summaries)

    print(f"\nSending to Telegram ({len(message)} chars)...")
    if send(message, cfg.telegram):
        print("Done!")
    else:
        print("Failed to send.")


if __name__ == "__main__":
    run()
