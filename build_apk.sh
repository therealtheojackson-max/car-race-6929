#!/bin/bash
# Build script for City Car Race APK
# This script builds the APK using Buildozer

echo "=========================================="
echo "City Car Race - APK Build Script"
echo "=========================================="
echo ""

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ buildozer not found. Installing..."
    pip install buildozer cython
fi

# Check if Java is installed (required for Android SDK)
if ! command -v java &> /dev/null; then
    echo "⚠️  Java not found. APK build requires Java."
    echo "Please install Java Development Kit (JDK) and try again."
    exit 1
fi

echo "✅ Dependencies found"
echo ""
echo "Building APK..."
echo "Note: This may take 10-30 minutes on first build"
echo ""

# Build for Android
buildozer android debug

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ APK Build Successful!"
    echo "=========================================="
    echo ""
    echo "APK location: bin/carrace-debug.apk"
    echo ""
    echo "To install on Android device:"
    echo "  1. Enable USB Debugging on your device"
    echo "  2. Connect device via USB"
    echo "  3. Run: adb install bin/carrace-debug.apk"
    echo ""
    echo "Or use Android Studio to install"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ APK Build Failed"
    echo "=========================================="
    echo ""
    echo "Try these steps:"
    echo "  1. Install Android SDK: buildozer android debug_build"
    echo "  2. Set ANDROID_SDK_ROOT and ANDROID_NDK_ROOT environment variables"
    echo "  3. Install Java Development Kit (JDK)"
    echo ""
    exit 1
fi
