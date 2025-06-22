#!/bin/bash
# Quick run script for LED Tomato CLI

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the CLI with all passed arguments
ledtomato "$@"
