#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run the main script
python -m adventure_generation.main ./sample_inputs/ariel_coast.txt ./sample_inputs/ariel_coast.jpg
