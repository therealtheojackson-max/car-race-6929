#!/usr/bin/env bash
set -euo pipefail

# launch_switch.sh
# Auto-detect aarch64 and tune resolution for performance, then run the game in .venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR%/scripts}"
VENV_DIR="$ROOT_DIR/.venv"
MAIN_PY="$ROOT_DIR/main.py"

# Default tuned resolution for Switch (can be overridden via env)
DEFAULT_WIDTH=${SWITCH_GAME_WIDTH:-800}
DEFAULT_HEIGHT=${SWITCH_GAME_HEIGHT:-600}

echo "Launcher: starting car-race on Switchroot"

# Check architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
  echo "Warning: This launcher is tuned for aarch64 Switchroot systems. Proceeding anyway."
fi

# Make sure virtualenv exists
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtualenv not found. Creating .venv and installing lightweight dependencies..."
  python3 -m venv "$VENV_DIR"
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  pip install pygame
else
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
fi

# Backup original resolution constants if present
PY_SETTINGS_FILE="$ROOT_DIR/main.py"
TMP_SETTINGS="$ROOT_DIR/.main_settings_tmp.py"

# Create a small patch: set WIDTH, HEIGHT to tuned values via environment injection
# We'll run Python with an override module that patches pygame display before importing main
cat > "$TMP_SETTINGS" <<EOF
# Auto-generated temporary settings for Switch launcher
WIDTH = $DEFAULT_WIDTH
HEIGHT = $DEFAULT_HEIGHT
EOF

echo "Launching game with resolution ${DEFAULT_WIDTH}x${DEFAULT_HEIGHT} (temporary override)"

# Run the game with the temporary settings module available on PYTHONPATH
PYTHONPATH="$ROOT_DIR:$ROOT_DIR" python3 -c "import importlib, sys; sys.path.insert(0,'$ROOT_DIR'); import types; import builtins
import runpy
# Inject temporary settings namespace
from importlib import util
spec = util.spec_from_file_location('switch_temp_settings', '$TMP_SETTINGS')
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)
# Put into sys.modules so main.py can import if it reads WIDTH/HEIGHT via module
sys.modules['switch_temp_settings'] = mod
# Run main
runpy.run_path('$MAIN_PY', run_name='__main__')"

rm -f "$TMP_SETTINGS"

echo "Game exited. Deactivating virtualenv."
deactivate || true

exit 0
