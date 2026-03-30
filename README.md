# npu-digest

Morning IT digest via Rockchip NPU (rkllama) + Telegram.

## Pipeline

```
RSS feeds → fetch articles → chunk text → rkllama (Qwen3-4B on NPU) → Telegram
```

## Requirements

- Orange Pi 5 Plus (RK3588) with rkllama running on port 8080
- Python 3.10+
- `feedparser`, `requests`, `beautifulsoup4`

## Setup

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml
# edit config.yaml
python -m src.digest
```

## Config

See `config.example.yaml`.
