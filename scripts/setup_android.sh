#!/bin/bash

# Complete Android SDK setup script for macOS
# This script sets up Android SDK, NDK, and related tools for building with buildozer

set -e

ANDROID_SDK_ROOT="$HOME/.buildozer/android/platform/android-sdk"
ANDROID_NDK_ROOT="$HOME/.buildozer/android/platform/android-ndk-r25b"

echo "Setting up Android SDK..."

# Create necessary directories
mkdir -p "$ANDROID_SDK_ROOT"/{cmdline-tools,platforms,build-tools,system-images}

# Download and extract cmdline-tools if needed
if [ ! -d "$ANDROID_SDK_ROOT/cmdline-tools/latest" ]; then
    echo "Downloading Android Command Line Tools..."
    cd /tmp
    curl -s -O https://dl.google.com/android/repository/commandlinetools-mac-6514223_latest.zip
    unzip -q commandlinetools-mac-6514223_latest.zip -d "$ANDROID_SDK_ROOT/cmdline-tools"
    mv "$ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools" "$ANDROID_SDK_ROOT/cmdline-tools/latest"
    rm commandlinetools-mac-6514223_latest.zip
fi

# Set up environment
export ANDROID_SDK_ROOT
export ANDROID_NDK_ROOT
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"

echo "ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT"
echo "ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"

# Accept SDK licenses
mkdir -p "$ANDROID_SDK_ROOT/licenses"
echo "Accepting Android SDK licenses..."
echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > "$ANDROID_SDK_ROOT/licenses/android-sdk-license"
echo "d56f5187479451eabf01fb78af6dfcb131b33910" > "$ANDROID_SDK_ROOT/licenses/android-sdk-preview-license"

echo "✓ Android SDK setup complete"
echo ""
echo "To use the SDK, run:"
echo "  export ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT"
echo "  export ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"
echo "  export PATH=\"\$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:\$PATH\""
