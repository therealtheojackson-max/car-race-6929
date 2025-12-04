#!/usr/bin/env bash
# Sign and zipalign an APK using a provided keystore.
# Usage:
#   ./scripts/sign_apk.sh <unsigned-apk-path> <keystore-path> <keystore-password> <key-alias> [<key-password>]

set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <unsigned-apk-path> <keystore-path> <keystore-password> <key-alias> [<key-password>]"
  exit 2
fi

UNSIGNED_APK="$1"
KEYSTORE="$2"
KS_PASS="$3"
KEY_ALIAS="$4"
KEY_PASS="${5:-$KS_PASS}"

if [ ! -f "$UNSIGNED_APK" ]; then
  echo "Unsigned APK not found: $UNSIGNED_APK"
  exit 1
fi

if [ ! -f "$KEYSTORE" ]; then
  echo "Keystore not found: $KEYSTORE"
  exit 1
fi

OUT_DIR=$(dirname "$UNSIGNED_APK")
BASE_NAME=$(basename "$UNSIGNED_APK" .apk)
ALIGNED="$OUT_DIR/${BASE_NAME}-aligned.apk"
SIGNED="$OUT_DIR/${BASE_NAME}-signed.apk"

# Find zipalign and apksigner on PATH, otherwise try common Android SDK locations
ZIPALIGN=$(command -v zipalign || true)
APKSIGNER=$(command -v apksigner || true)

if [ -z "$ZIPALIGN" ] || [ -z "$APKSIGNER" ]; then
  # try ANDROID_SDK_ROOT build-tools (common)
  if [ -n "${ANDROID_SDK_ROOT:-}" ]; then
    BT=$(ls -d "$ANDROID_SDK_ROOT"/build-tools/* 2>/dev/null | sort -V | tail -n1 || true)
    if [ -n "$BT" ]; then
      ZIPALIGN="$BT/zipalign"
      APKSIGNER="$BT/apksigner"
    fi
  fi
fi

if [ ! -x "$ZIPALIGN" ] || [ ! -x "$APKSIGNER" ]; then
  echo "zipalign or apksigner not found. Install Android build-tools or ensure they are on PATH."
  exit 1
fi

echo "Zipaligning..."
"$ZIPALIGN" -v -p 4 "$UNSIGNED_APK" "$ALIGNED"

echo "Signing..."
"$APKSIGNER" sign --ks "$KEYSTORE" --ks-pass pass:"$KS_PASS" --key-pass pass:"$KEY_PASS" --out "$SIGNED" "$ALIGNED"

echo "Verifying signature..."
"$APKSIGNER" verify --print-certs "$SIGNED" && echo "Signed APK: $SIGNED"

echo "Done."

exit 0
