#!/usr/bin/env bash
# build.sh

set -o errexit
set -o verbose

echo "=== Installing System Dependencies ==="
apt-get update
apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    libtesseract-dev \
    libleptonica-dev

echo "=== Verifying Tesseract Installation ==="
which tesseract
tesseract --version

echo "=== Installing Python Dependencies ==="
pip install -r requirements.txt

echo "=== Build Completed ==="