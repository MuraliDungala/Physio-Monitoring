#!/bin/bash
set -e

# Force Python 3.11
export PYENV_VERSION=3.11.9

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
