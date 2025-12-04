[app]

# (str) Title of your application
title = City Car Race

# (str) Package name
package.name = carrace

# (str) Package domain (needed for android/ios packaging)
package.domain = org.carrace

# (source.dir) Source code where the main.py live
source.dir = .

# (list) Application requirements
# NOTE: This project uses pygame. Packaging pygame on Android may require
# a compatible recipe (pygame_sdl2 or a p4a pygame recipe). You may need
# to adjust this value or port to Kivy for smoother packaging.
requirements = python3,pygame

# (source.include_exts) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (source.exclude_patterns) Patterns to exclude from the source
source.exclude_patterns = tests,bin,buildozer.spec,*.pyc,test_*.py,chat_server.py

# (list) Source files to include (let empty to include all the files)
source.include_patterns = main.py,accounts.json,banned_users.json,warnings.json,moderation_config.json

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / APPBundle will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Pattern to whitelist for the whole project
android.whitelist = lib-dynload/termios.so

# (list) This is a list of keywords corresponding to the permitted internet
# permissions of the application.
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / APPBundle will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Pattern to whitelist for the whole project
android.whitelist = lib-dynload/termios.so

# (list) This is a list of keywords corresponding to the permitted internet
# permissions of the application.
android.permissions = INTERNET

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# Display warning when buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# Path to build artefact storage, absolute or relative to spec file
build_dir = .buildozer

# Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
