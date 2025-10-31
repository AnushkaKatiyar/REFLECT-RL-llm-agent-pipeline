#!/bin/bash
source .venv/bin/activate
export OPENAI_API_KEY="ollama"
export OPENAI_BASE_URL="http://localhost:11434/v1"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Running Reflexion local test..."
python simple.py --model codellama:7b-instruct --num_problems 2 --verbose
