#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run the main script
python -m adventure_generation.main ./sample_inputs/ariel_coast.txt ./sample_inputs/ariel_coast.jpg ./sample_inputs/styles.json
#python -m adventure_generation.main ./sample_inputs/LoneTreeCrossing.txt ./sample_inputs/LoneTreeCrossing.jpg ./sample_inputs/styles.json
