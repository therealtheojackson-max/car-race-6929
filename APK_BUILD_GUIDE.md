# APK Build Guide

## Overview
This guide explains how to build and deploy the City Car Race game as an Android APK (Android Package).

## Prerequisites

### Required Software
- **Python 3.8+** - Programming language
- **Java Development Kit (JDK)** - Required for Android tools
  - Version 8 or higher (JDK 11+ recommended)
  - [Download here](https://www.oracle.com/java/technologies/downloads/)
  
- **Android SDK** - Downloaded automatically by buildozer
  - Requires ~5-10 GB disk space
  - Takes 10-30 minutes on first build

### Installation Steps

#### 1. Install Java (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openjdk-11-jdk openjdk-11-jdk-headless
```

**macOS:**
```bash
brew install openjdk@11
# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 11)
```

**Windows:**
- Download from [Oracle Java](https://www.oracle.com/java/technologies/downloads/)
- Run installer and follow prompts
- Add Java bin directory to system PATH

#### 2. Install Python Build Tools

```bash
pip install --upgrade pip
pip install buildozer cython
```

#### 3. Install Additional Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install -y \
    build-essential \
    ccache \
    git \
    libncurses5:i386 \
    libstdc++6:i386 \
    libz1:i386 \
    openjdk-11-jdk \
    openjdk-11-jdk-headless \
    unzip \
    zlib1g-dev \
    zlib1g:i386
```

**macOS:**
```bash
brew install ccache libtool libffi openssl
```

## Building the APK

### Quick Build

```bash
# Navigate to project directory
cd /workspaces/car-race

# Run build script
bash build_apk.sh
```

### Manual Build

```bash
# Initialize buildozer (first time only)
buildozer android api

# Build debug APK
buildozer android debug

# Build release APK (requires signing)
buildozer android release
```

### Build Output

- **Debug APK:** `bin/carrace-debug.apk` (~50-100 MB)
- **Release APK:** `bin/carrace-release-unsigned.apk` (requires signing)

## Installation on Android Device

### Option 1: Via ADB (Android Debug Bridge)

```bash
# Install ADB tools
# Ubuntu/Debian: sudo apt-get install android-tools-adb
# macOS: brew install android-platform-tools

# Enable USB Debugging on device:
# Settings > Developer Options > USB Debugging (enable)

# Connect device via USB and run:
adb install bin/carrace-debug.apk

# Launch game:
adb shell am start -n org.carrace.carrace/org.kivy.android.PythonActivity
```

### Option 2: Manual Installation

1. Connect Android device to computer via USB
2. Enable "File Transfer" mode on device
3. Transfer `bin/carrace-debug.apk` to device
4. Use file manager on device to run installer
5. Grant permissions and launch

### Option 3: Android Studio

1. Open Android Studio
2. Go to: Run > Run 'app'
3. Select connected device
4. Choose APK file from `bin/` directory

## Server Configuration for Mobile

For multiplayer features on mobile devices:

### If Chat Server is on Local Network

Edit `main.py` line 284 (in ChatClient `__init__`):
```python
# Change from:
self.host = '127.0.0.1'  # localhost

# To your computer's IP (e.g., 192.168.1.100):
self.host = '192.168.1.100'
```

### If Chat Server is on Internet

Update ChatClient to use your public IP or domain name:
```python
self.host = 'your-domain.com'  # or public IP
```

Start chat server accessible to mobile:
```bash
# Listen on all interfaces
python chat_server.py
```

## Troubleshooting

### "buildozer not found"
```bash
pip install --upgrade buildozer cython
```

### "Java not found"
Ensure Java is installed and JAVA_HOME is set:
```bash
java -version
echo $JAVA_HOME
```

### Build hangs on "Downloading Android SDK"
- First build takes time (10-30 minutes)
- Ensure stable internet connection
- Can resume if interrupted: `buildozer android debug`

### Permission denied on APK install
```bash
chmod +x bin/carrace-debug.apk
```

### APK crashes on launch
Check logs with:
```bash
adb logcat | grep carrace
```

### Chat server connection issues on mobile
- Verify server is running: `ps aux | grep chat_server`
- Check firewall allows port 50007
- Verify mobile device is on same network
- Test connection: `adb shell nc -zv <server-ip> 50007`

## Performance Notes

- **First build:** 20-30 minutes (downloads SDK/NDK)
- **Subsequent builds:** 5-10 minutes
- **APK size:** 50-100 MB (includes Pygame and Python runtime)
- **Device requirements:** Android 5.0+ (API 21+)
- **RAM:** 2GB+ for smooth gameplay

## File Structure

```
/workspaces/car-race/
├── main.py                 # Game client
├── chat_server.py          # Chat server (runs on desktop)
├── buildozer.spec          # Build configuration
├── build_apk.sh            # Build script
├── requirements.txt        # Python dependencies
├── .buildozer/             # Build artifacts (auto-created)
└── bin/                    # APK output directory
    └── carrace-debug.apk   # Final APK file
```

## Next Steps

1. Build the APK using `bash build_apk.sh`
2. Install on Android device
3. Configure chat server IP if using multiplayer
4. Launch game and enjoy!

## Support

For issues or questions:
- Check Android Studio's device logs: `adb logcat`
- Verify Java installation: `java -version`
- Ensure buildozer is updated: `pip install --upgrade buildozer`
- Check buildozer logs: `buildozer android debug 2>&1 | tail -100`
