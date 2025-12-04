# Running City Car Race on a Nintendo Switch (Switchroot Linux)

This document explains the practical, realistic ways to run the game on a Nintendo Switch. There are two main approaches:

1) Run under Switchroot / Linux (recommended, easiest)
2) Native Switch homebrew port (harder — requires porting to libnx/devkitPro)

## 1) Switchroot (Linux) — Recommended path

Prerequisites:
- Switchroot (Ubuntu/Debian) already installed on your Switch, or another Linux rootfs (aarch64) that gives you a shell and apt
- SSH or terminal access to your Switch
- Enough free storage and a charged battery

What to do (summary):
1. Copy this project to the Switch (git clone or scp).
2. Run the helper script `scripts/install_switch_dependencies.sh` to install Python, Pygame and build dependencies.
3. Activate the virtualenv and run `python main.py`.

Why this works:
- `pygame` uses SDL2 and will run on Linux on Tegra (Switch's SoC) assuming you have the right dev libs and Python
- Your controller support is already implemented (GamepadHandler) and will map controllers visible to the OS

Limitations and caveats:
- Performance: The Switch is not as powerful as a desktop; performance depends on Switchroot kernel, GPU drivers and compositor.
- Display: You might need to tweak `WIDTH`/`HEIGHT` in `main.py` to match your display or to reduce resolution for performance.
- Input passthrough: If another process (like an emulator) is capturing the controller, it may not be visible to the game. Use Steam/BetterJoy or ensure the controller is bound to the OS.

## Launcher and Packaging (Added)

This repository includes two new helper scripts in `scripts/` to make running and installing easier on Switchroot:

- `scripts/launch_switch.sh` — a launcher that:
	- Detects CPU architecture and prints it
	- Creates/uses `.venv` if missing
	- Temporarily overrides resolution to a Switch-friendly size (default 800x600)
	- Activates the virtualenv and runs `main.py`

- `scripts/build_deb.sh` — a simple helper to create a minimal `.deb` package which installs the project under `/opt/car-race` and creates a `/usr/local/bin/car-race` symlink to the launcher.

Usage examples:

```bash
# Prepare runtime and run the game (on the Switch):
cd ~/car-race
bash scripts/install_switch_dependencies.sh
bash scripts/launch_switch.sh

# Build a .deb (on-device or cross-build environment):
cd car-race
bash scripts/build_deb.sh
sudo dpkg -i car-race_0.1_$(dpkg --print-architecture).deb
```

Notes:
- The launcher temporarily injects a small Python module to override `WIDTH`/`HEIGHT` at runtime to avoid editing `main.py`. You can set `SWITCH_GAME_WIDTH` and `SWITCH_GAME_HEIGHT` environment variables to change the defaults.
- The `.deb` script is intentionally minimal: it packages the source under `/opt/car-race`. You may want to customize the packaging (dependencies, icon, desktop entry) for a nicer install experience.

## 2) Native homebrew port (libnx / devkitPro)

This is a full port to Nintendo Switch homebrew. It requires:
- Converting the Python/pygame code to C/C++ or using a Python runtime that can be bundled (very complex)
- Using `libnx` + `SDL2` built for the Switch (devkitPro) to render and accept input
- Rewriting platform-specific bits (file paths, network code) and packaging assets

Steps (high level):
1. Export game assets (images, sounds) and rewrite the game loop using SDL2 in C/C++.
2. Build with devkitPro/libnx and test on a modded Switch with Atmosphere.

This route is advanced; it typically requires a C/C++ developer and substantial time.

## Android / Waydroid approach

Some users ask to run Android apps (APK) on Switch via Waydroid/Anbox. This requires kernel support for binder and ashmem and is **not** guaranteed on Switchroot kernels. If you need Android-only apps, it's usually easier to run them on a phone/tablet or PC.

## Commands to run on the Switch (summary)

Copy repository to the device:

```bash
# On your host machine
git clone <repo-url>
scp -r car-race/ switch:/home/youruser/

# On the Switch (ssh into it)
cd car-race
bash scripts/install_switch_dependencies.sh
source .venv/bin/activate
python main.py
```

## Tuning tips
- Reduce `WIDTH` and `HEIGHT` in `main.py` to 800x600 or 720x480 for better FPS.
- Turn off non-essential visual effects in the game if you add quality toggles.
- Use a wired controller or a well-supported Bluetooth driver.

## Next steps I can help with
- Add a small launcher script to automatically tune resolution on aarch64
- Add an optional MAKEFILE or package script to build a `.deb` for easier install
- Provide a checklist to enable binder/ashmem on custom kernels (dangerous — advanced only)

If you want to proceed, tell me:
- Do you have Switchroot already installed? (Yes/No)
- Do you want me to add a resolution-tuning launcher and a `.deb` packaging script?