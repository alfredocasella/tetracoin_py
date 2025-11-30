#!/bin/bash

# Build script for TetraCoin Android APK with buildozer
# This script handles SSL certificate issues on macOS with Python 3.12

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set SSL certificate path from certifi
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")

echo "Using certificates from: $SSL_CERT_FILE"
echo "Starting Android build..."

# Run buildozer
buildozer android debug "$@"
