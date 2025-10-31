#!/bin/bash
source .venv/bin/activate

export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="http://localhost:11434/v1"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "🚀 Running full Reflexion benchmark with CodeLlama..."

python main.py \
  --run_name "reflexion_local_codellama_full" \
  --root_dir "root" \
  --dataset_path ./benchmarks/humaneval-py.jsonl \
  --strategy "reflexion" \
  --language "py" \
  --model "codellama:7b-instruct" \
  --pass_at_k "1" \
  --max_iters "3" \
  --verbose | tee reflexion_full_run.lo g

