import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class TelegramConfig:
    bot_token: str
    chat_id: int


@dataclass
class RkllamaConfig:
    url: str = "http://127.0.0.1:8080"
    model: str = "qwen3-4b-instruct-npu"
    max_tokens: int = 512
    temperature: float = 0.7


@dataclass
class FeedConfig:
    name: str
    url: str
    max_items: int = 5


@dataclass
class DigestConfig:
    chunk_size: int = 1500
    max_article_words: int = 3000


@dataclass
class Config:
    telegram: TelegramConfig
    rkllama: RkllamaConfig
    feeds: List[FeedConfig]
    digest: DigestConfig


def load_config(path: str = "config.yaml") -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)

    return Config(
        telegram=TelegramConfig(**data["telegram"]),
        rkllama=RkllamaConfig(**data.get("rkllama", {})),
        feeds=[FeedConfig(**f) for f in data.get("feeds", [])],
        digest=DigestConfig(**data.get("digest", {})),
    )
