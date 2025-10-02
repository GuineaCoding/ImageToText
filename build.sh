#!/usr/bin/env bash
# build.sh

set -o errexit

echo "Installing system dependencies..."
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng
echo "Tesseract installation completed"

# Verify installation
which tesseract
tesseract --version