#!/bin/bash

# Batch automation for Reflexion: runs from 35 to 161 in steps of 5

for i in $(seq 35 5 160); do
  end=$((i+5))
  echo "🚀 Running problems $i to $end ..."

  # Run the batch
  python main.py \
    --run_name "reflexion_codellama_35_161" \
    --root_dir "root" \
    --dataset_path ./benchmarks/humaneval-py.jsonl \
    --strategy "reflexion" \
    --language "py" \
    --model "codellama:7b-instruct" \
    --pass_at_k 1 \
    --max_iters 3 \
    --verbose \
    --start_from $i \
    --end_at $end

  echo "✅ Completed problems $i to $end."

  # --- Restart Ollama cleanly ---
  echo "🔁 Restarting Ollama safely..."

  # Kill any existing Ollama processes
  pkill -9 -f "ollama serve" 2>/dev/null || true
  sleep 8

  # Wait until port 11434 is actually free
  while lsof -i :11434 >/dev/null 2>&1; do
    echo "🕒 Waiting for port 11434 to free up..."
    sleep 3
  done

  echo "🔄 Starting fresh Ollama server..."
  nohup ollama serve >/dev/null 2>&1 &
  sleep 20
done

echo "🎉 All batches from 35–161 completed successfully!"
