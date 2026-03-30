#!/bin/bash
# Start rkllama, run digest, unload model and stop service

echo "[$(date)] Starting rkllama..."
systemctl --user start rkllama

# Wait for server ready (max 60s)
for i in $(seq 1 30); do
    curl -s http://localhost:8080/api/version > /dev/null 2>&1 && break
    sleep 2
done
echo "[$(date)] rkllama ready"

echo "[$(date)] Running digest..."
cd /home/orangepi/npu-digest
python3 -m src.digest >> /tmp/npu-digest.log 2>&1

echo "[$(date)] Unloading model and stopping rkllama..."
curl -s -X POST http://localhost:8080/unload_model \
    -H "Content-Type: application/json" \
    -d '{"model_name": "qwen3-4b-instruct-npu"}' > /dev/null 2>&1
sleep 2
systemctl --user stop rkllama

echo "[$(date)] Done. RAM freed."
