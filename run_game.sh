#!/bin/bash

# Gravity Wells Game Runner
# This script runs the game with the correct Python environment

cd "$(dirname "$0")"

if [ -f ".venv/bin/python" ]; then
    echo "Starting Gravity Wells..."
    .venv/bin/python main.py
else
    echo "Virtual environment not found. Please run: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
fi
