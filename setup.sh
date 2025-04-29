#!/usr/bin/env bash
# -----------------
# This will only work for debian relative distributions, for other replicate steps manually

# Update package list
sudo apt-get update 

# Install python module - venv
sudo apt install -y python3.10-venv

# Create virtual environment
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt