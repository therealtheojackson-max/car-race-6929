#!/usr/bin/env bash
set -euo pipefail

# build_deb.sh
# Simple script to create a Debian package for the `car-race` game on Debian-like Switchroot
# This creates a minimal package that installs the project into /opt/car-race and a systemd user service

PKG_NAME="car-race"
PKG_VERSION="0.1"
PKG_ARCH=$(dpkg --print-architecture || echo "arm64")
PKG_MAINTAINER="car-race <noreply@example.com>"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/deb_build"
INSTALL_DIR="$BUILD_DIR/opt/$PKG_NAME"
DEBIAN_DIR="$BUILD_DIR/DEBIAN"

rm -rf "$BUILD_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$DEBIAN_DIR"

# Copy project files (exclude large/unneeded files if required)
rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' "$ROOT_DIR/" "$INSTALL_DIR/"

# Control file
cat > "$DEBIAN_DIR/control" <<EOF
Package: $PKG_NAME
Version: $PKG_VERSION
Section: games
Priority: optional
Architecture: $PKG_ARCH
Maintainer: $PKG_MAINTAINER
Description: City Car Race - Python pygame game (Switchroot package)
EOF

# Postinst: create symlink and optionally create a systemd user service template
cat > "$DEBIAN_DIR/postinst" <<'EOF'
#!/bin/sh
set -e
# Create system-wide symlink to /usr/local/bin/car-race
ln -sf /opt/car-race/scripts/launch_switch.sh /usr/local/bin/car-race || true
chmod +x /usr/local/bin/car-race || true
EOF
chmod 755 "$DEBIAN_DIR/postinst"

# Prerm: remove symlink
cat > "$DEBIAN_DIR/prerm" <<'EOF'
#!/bin/sh
set -e
rm -f /usr/local/bin/car-race || true
EOF
chmod 755 "$DEBIAN_DIR/prerm"

# Build package
fakeroot dpkg-deb --build "$BUILD_DIR" "$ROOT_DIR/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"

echo "Built: $ROOT_DIR/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"
exit 0
