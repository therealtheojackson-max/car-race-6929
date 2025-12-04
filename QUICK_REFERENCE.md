# QUICK REFERENCE CARD

## 🎮 Game Controls

### Desktop (Keyboard)
- **WASD** / **Arrow Keys** - Move car
- **F** - Take ferry
- **O** - Toggle online mode
- **T** - Open chat
- **H** - Open home
- **R** - Restart (game over)
- **ESC** - Quit

### Gamepad/Controller (NEW! ✨)
- **Left Analog Stick** - Move car
- **X Button** - Take ferry
- **Y Button** - Open home
- **RB Button** - Open garage
- **LB Button** - Open shop
- **RT Button** - Chat
- **B Button** - Cancel/Close menus
- **A Button** - Confirm/Restart
- **D-Pad** - Menu navigation
- **See CONSOLE_CONTROLLER_GUIDE.md for full mapping**

### Mobile
- **▲▼◄►** buttons - Move car
- **F** button - Ferry
- **Touch** - Interact with NPCs

---

## 🚀 Quick Start

### Run Locally
```bash
# Terminal 1: Start chat server
python chat_server.py

# Terminal 2: Start game (with/without controller)
python main.py
```

### Build Mobile APK
```bash
bash build_apk.sh
adb install bin/carrace-debug.apk
```

---

## 🔐 Accounts

**Login Screen:**
- **Tab** - Switch LOGIN/REGISTER
- **↑↓** - Switch username/password
- **Enter** - Submit
- **ESC** - Skip (offline mode)

**With Gamepad:**
- **D-Pad UP/LEFT** - Switch to LOGIN
- **D-Pad DOWN/RIGHT** - Switch to REGISTER
- **A Button** - Submit
- **B Button** - Offline mode

**Requirements:**
- Username: 3+ characters
- Password: 4+ characters


---

## 💬 Chat System

**Connection:**
- Press **O** to connect (requires account)
- Type **T** to chat
- Messages broadcast to all players

**Moderation:**
- 🚫 Bullying (5 terms) = Instant ban
- ⚠️ Inappropriate (2 terms) = Warning + censor
- 3 warnings = Automatic ban

---

## 📦 Files Overview

| File | Purpose |
|------|---------|
| `main.py` | Game engine + UI |
| `chat_server.py` | Chat server |
| `buildozer.spec` | APK config |
| `build_apk.sh` | Build script |
| `accounts.json` | User accounts |
| `moderation_config.json` | Chat settings |

---

## 🧪 Testing

```bash
python test_full_integration.py   # All tests
python test_accounts.py            # Accounts only
python smoke_check.py              # Game logic
```

---

## 📱 Mobile Setup

1. **Build:** `bash build_apk.sh`
2. **Install:** `adb install bin/carrace-debug.apk`
3. **Configure:** Edit `main.py` line 284 for server IP
4. **Run:** Launch "City Car Race" on device

---

## 🎯 Game Features

- 4 islands + ferries
- 4 car models ($500-$5000)
- 4 house tiers (upgradeable)
- 6 decoration items
- 4 racing difficulties
- Online multiplayer chat
- Moderation system
- Account system

---

## 📝 Documentation

- **README.md** - Main guide
- **APK_BUILD_GUIDE.md** - Build instructions
- **ACCOUNT_SYSTEM.md** - Auth details
- **IMPLEMENTATION_SUMMARY.md** - Full features

---

## ⚙️ Server Config

Default: `localhost:50007`

For mobile: Edit `main.py` line 284
```python
self.host = '192.168.1.100'  # Your computer's IP
```

---

## 🔧 Troubleshooting

**Server won't start:** `python chat_server.py` check port 50007

**APK build fails:** Install Java + buildozer: `pip install buildozer cython`

**Game won't connect:** Ensure server running + correct IP in code

**Chat not working:** Login required - use register/login screen

---

## 📊 Performance

- Chat latency: <50ms (local)
- APK size: 50-100 MB
- Minimum RAM: 2GB
- Supported Android: 5.0+ (API 21+)

---

**Status: ✅ READY TO DEPLOY**
