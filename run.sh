#!/bin/bash
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

python -m adventure_generation.main $1 $2 $3
