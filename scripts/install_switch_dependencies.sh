#!/usr/bin/env bash
set -euo pipefail

# install_switch_dependencies.sh
# Helper script to install Python + Pygame + build deps on a Debian/Ubuntu Switchroot
# Run on the Switchroot Linux shell (ssh into the Switch or run in terminal on device)

echo "Checking for sudo..."
if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo not found — please run as root or install sudo. Exiting."
  exit 1
fi

echo "Updating package lists..."
sudo apt-get update

echo "Installing system build dependencies (may take a while)..."
sudo apt-get install -y --no-install-recommends \
  build-essential python3-dev python3-pip python3-venv \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libfreetype6-dev libavformat-dev libavcodec-dev libswscale-dev \
  libjpeg-dev libpng-dev pkg-config \
  git wget curl

# Some distros provide python3-pygame as a package; try that first for speed
if apt-cache show python3-pygame >/dev/null 2>&1; then
  echo "Installing python3-pygame from apt"
  sudo apt-get install -y python3-pygame || true
fi

# Create venv and install Python requirements
if [ ! -d ".venv" ]; then
  echo "Creating virtualenv .venv"
  python3 -m venv .venv
fi

echo "Activating virtualenv and installing requirements..."
# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip and wheel
pip install --upgrade pip setuptools wheel

# If project has requirements.txt, install from it; otherwise install pygame
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  pip install pygame
fi

echo "Installation complete. To run the game in the venv:"
echo "  source .venv/bin/activate"
echo "  python main.py"

# Check for binder/ashmem (only needed for Android runtime like Waydroid)
if [ -e /dev/binder ] || ls /dev/binder* 2>/dev/null | grep -q binder; then
  echo "binder device present"
else
  echo "binder device not found; Android runtime (Waydroid/Anbox) likely won't work without kernel changes"
fi

if [ -e /dev/ashmem ] || ls /dev/ashmem* 2>/dev/null | grep -q ashmem; then
  echo "ashmem device present"
else
  echo "ashmem device not found; Android runtime (Waydroid/Anbox) likely won't work without kernel changes"
fi

# Print some helpful checks
echo
echo "Quick checks:"
uname -a
cat /etc/os-release || true
arch || true

echo "Done."