# car-race

A comprehensive top-down car racing game with online multiplayer chat, account system, and extensive progression mechanics.

## Features

- **Multi-Island City System**: 4 islands connected by ferries
- **Racing System**: 4 difficulty levels with progressive rewards ($200-$1500)
- **Economy System**: 
  - Earn currency from racing and distance
  - 4 car models to purchase ($500-$5000)
  - Garage shops on each island
- **Home System**: 4 house tiers with decoration placement
- **Decoration Shop**: 6 decorative items to customize your home
- **Online Chat**: TCP-based multiplayer chat with moderation
- **Account System**: User registration and login with password hashing
- **Moderation**: Automatic ban/warn system for inappropriate content
- **Adaptive Controls**: WASD/touch buttons based on device type

## Setup

1. Create and activate a Python virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the chat server (in a separate terminal):

```bash
python chat_server.py
```

This will start the TCP chat server on `localhost:50007` and load moderation config.

4. Run the game:

```bash
python main.py
```

## Game Controls

### Keyboard (Desktop)
- **WASD**: Move car (or Arrow keys)
- **F**: Take ferry to another island
- **O**: Connect/disconnect from online chat
- **T**: Open chat input (when online)
- **H**: Open home to place decorations
- **R**: Restart after game over
- **ESC**: Quit game

### Touch (Mobile)
- On-screen buttons for movement and ferry
- Tap to interact with NPCs and shops

## Account System

### Login Screen
When you start the game, you'll see a login screen:
- **Username**: 3+ characters required
- **Password**: 4+ characters required
- **Tab**: Switch between Login and Register modes
- **Up/Down**: Switch between username/password fields
- **Enter**: Submit
- **ESC**: Skip (play offline)

### Features
- New accounts stored with SHA256 password hashing
- Persistent account data in `accounts.json`
- Automatic login on game start with valid credentials
- Offline mode available if you skip authentication

## Chat System

### Connection
- Press **O** to toggle online mode (requires account)
- Server automatically sends auth_required message
- Player must authenticate before accessing chat

### Usage
- Press **T** to open chat input
- Type your message
- Press **Enter** to send
- Press **ESC** to cancel

### Moderation
- **Bullying terms** (idiot, stupid, kill, die, hate): Immediate permanent ban
- **Inappropriate terms** (damn, crap): Warning + message censoring
- **3 warnings**: Automatic permanent ban
- **Admin commands**: temp_ban, unban, ban, list_bans, etc.

Moderation settings are configurable in `moderation_config.json`.

## Files

- `main.py` (1200+ lines): Core game with all gameplay systems
- `chat_server.py` (400+ lines): TCP chat server with moderation
- `moderation_config.json`: Tunable moderation parameters
- `accounts.json`: Persisted user accounts with password hashes
- `banned_users.json`: Banned users (permanent or temp bans)
- `warnings.json`: Per-user warning counters
- `smoke_check.py`: Headless test suite for game mechanics
- `test_accounts.py`: Account system test suite
- `test_system.py`: Comprehensive system test

## Architecture

- **Game Client**: Pygame-based UI with ChatClient for TCP communication
- **Chat Server**: TCP socket server with broadcast messaging and moderation
- **Persistence**: JSON-based storage for accounts, bans, warnings, and config

## Testing

Run the smoke check to verify all systems:

```bash
python smoke_check.py
```

Test the account system:

```bash
python test_accounts.py
```

Run comprehensive system test:

```bash
python test_system.py
```

## Development Notes

- Password hashing uses SHA256 (production would use bcrypt)
- Chat uses line-delimited JSON protocol (newline separator)
- Ban expiry is checked on login and periodically cleaned
- All data is stored in simple JSON files (production would use a database)

## Building APK for Android

### Requirements
- Python 3.8+
- Java Development Kit (JDK) 8 or higher
- Android SDK (will be downloaded by buildozer)
- buildozer and cython

### Installation

1. Install build dependencies:

```bash
pip install buildozer cython
```

2. Install Java Development Kit:

On Ubuntu/Debian:
```bash
sudo apt-get install openjdk-11-jdk
```

On macOS:
```bash
brew install openjdk@11
```

3. Build the APK:

```bash
# Using the build script
bash build_apk.sh

# Or manually
buildozer android debug
```

The first build may take 20-30 minutes as it downloads the Android SDK and NDK.

### APK Output

After a successful build, the APK will be located at:
```
bin/carrace-debug.apk
```

### CI (GitHub Actions)

This repository includes a workflow that attempts to build the APK in CI: `.github/workflows/build_apk.yml`.
It runs Buildozer on an Ubuntu runner and uploads any generated APK as an artifact. Use the Actions tab to trigger the workflow (or push to `main`).

Note: CI builds may still fail due to pygame packaging issues — see the notes above about pygame vs Kivy and p4a recipes.

### Signing and uploading to Akpure

To publish to Akpure you must upload a release-signed APK. Two approaches are supported:

- Local signing (no secrets shared): build an unsigned/release APK locally and sign it with your keystore using `zipalign` and `apksigner`.
- CI signing (automated): store your keystore in GitHub Secrets (base64-encoded) and the workflow will sign the produced APK and upload the signed APK as an artifact.

Local signing example (after building with Buildozer):

```bash
# generate a keystore if you don't have one
keytool -genkey -v -keystore release-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias mykey

# build release (unsigned) with Buildozer
buildozer android release

# sign using helper script (requires Android build-tools on PATH or ANDROID_SDK_ROOT set)
./scripts/sign_apk.sh bin/carrace-release-unsigned.apk release-keystore.jks <keystore-password> mykey

# result: bin/carrace-release-unsigned-signed.apk (or similar)
```

CI signing (GitHub Actions):

1. Create three repository secrets: `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_PASSWORD` (if different from keystore password). `KEYSTORE_BASE64` should contain your keystore file encoded with base64, e.g.:

```bash
base64 release-keystore.jks | pbcopy   # or use redirect to a file
```

2. Push to `main` or run the `Build APK (Buildozer)` workflow; if the secrets are present the workflow will decode the keystore, sign the produced APK, and upload the signed APK as an artifact.

Uploading to Akpure

1. Create an account on https://akpure.com and follow their upload flow.
2. Upload the signed APK (`bin/*-signed.apk`) and fill metadata.

Security note: Keep your keystore private; do not commit it into the repository. Use GitHub Secrets for CI signing.

### Installing on Android Device

1. Enable USB Debugging on your Android device (Settings > Developer Options)
2. Connect device via USB cable
3. Install using ADB:

```bash
adb install bin/carrace-debug.apk
```

Or transfer the APK file and install manually on the device.

### Notes

- The APK includes the game engine (Pygame) but the chat server runs separately
- For multiplayer features, you'll need to run `chat_server.py` on a networked computer
- Configure the server IP in the game settings or modify the ChatClient host parameter
- Mobile controls are automatically enabled for touch devices

Enjoy the game!
