# Nintendo Switch & Console Controller Support

## ✅ OVERVIEW

The car race game now supports **Nintendo Switch Pro Controllers**, **Xbox controllers**, **PlayStation controllers**, and **any standard console gamepad** connected via USB or Bluetooth!

- **Left Analog Stick**: Control car movement (forward/back/left/right)
- **D-Pad**: Menu navigation
- **Action Buttons**: Game controls
- **Triggers**: Special actions
- **Full keyboard fallback**: If no controller is detected

---

## 🎮 SUPPORTED CONTROLLERS

### Nintendo Switch
- **Nintendo Switch Pro Controller** ✅
- **JoyCon Controllers** (when paired in grip) ✅

### Xbox
- **Xbox One Controller** ✅
- **Xbox Series X/S Controller** ✅
- **Xbox 360 Controller** ✅

### PlayStation
- **PlayStation 5 DualSense** ✅
- **PlayStation 4 DualShock 4** ✅

### Generic
- **Any USB HID compliant gamepad** ✅

---

## 🕹️ CONTROL MAPPING

### DRIVING (Main Game)

| Control | Action | Gamepad | Keyboard |
|---------|--------|---------|----------|
| Move Forward | Go up | Left Stick Up | W |
| Move Backward | Go down | Left Stick Down | S |
| Move Left | Turn left | Left Stick Left | A |
| Move Right | Turn right | Left Stick Right | D |

**Deadzone**: 0.3 (stick must move 30% before registering)

---

### ACTION BUTTONS (Main Game)

| Action | Gamepad | Keyboard |
|--------|---------|----------|
| Take Ferry | X Button | F |
| Enter Home | Y Button | H |
| Open Garage | RB Button | G |
| Open Shop | LB Button | S |
| Chat (toggle) | RT Button | T |
| Cancel/Close Menu | B Button | ESC |
| Restart (after game over) | A Button | R |

---

### D-PAD (Menu Navigation)

| Action | Gamepad | Keyboard |
|--------|---------|----------|
| Up/Left | D-Pad Up/Left | Arrow Keys |
| Down/Right | D-Pad Down/Right | Arrow Keys |

---

## 📸 CAMERA APP CONTROLS

When inside your home at the computer:

| Action | Gamepad | Keyboard |
|--------|---------|----------|
| **Record/Stop** | Y Button or A Button | SPACE |
| **Toggle Library** | X Button | L |
| **Upload Video** | RT Button | ENTER |
| **Delete Video** | LB Button | DELETE |
| **Close Camera** | B Button | ESC |

---

## 🔐 LOGIN SCREEN CONTROLS

When logging in or registering:

| Action | Gamepad | Keyboard |
|--------|---------|----------|
| **Switch to Login** | D-Pad UP/LEFT | TAB |
| **Switch to Register** | D-Pad DOWN/RIGHT | TAB |
| **Submit** | A Button | ENTER |
| **Back to Offline** | B Button | ESC |

---

## 🔌 CONNECTION & SETUP

### Windows/Linux/Mac Setup

1. **Connect your controller** via USB or Bluetooth
2. **Start the game** - it will auto-detect your controller
3. **Check console output** - you should see:
   ```
   Gamepad detected: Xbox 360 Controller
   ```

### If No Controller Detected

The game will **automatically fall back to keyboard controls**:
- You can still play with WASD and function keys
- No controller required!

### Reconnect Controllers

If you disconnect and reconnect a controller mid-game:
- The game detects the reconnection automatically
- No need to restart!

---

## 🎯 BUTTON LAYOUT COMPARISON

### Nintendo Switch Pro Controller

```
              Y
          LB  □  RB
           ╱   △   ╲
    L Stick    START   RT (triggers)
              X  ▽
```

### Xbox Controller

```
              Y
          LB  □  RB
           ╱   △   ╲
    L Stick    MENU   RT (triggers)
              X  ▽
```

### PlayStation 5 DualSense

```
              △
          L1  □  R1
           ╱   ○   ╲
    L Stick    OPTIONS   R2 (triggers)
              X  ▽
```

### Generic Gamepad

```
    Buttons:  0=A, 1=B, 2=X, 3=Y
    Triggers: LT=4, RT=5
    Bumpers:  LB=4, RB=5
    Start/Back available
```

---

## 📊 TECHNICAL DETAILS

### GamepadHandler Class

The game includes a robust `GamepadHandler` class that:

- **Auto-detects** connected gamepads at startup
- **Re-detects** if controller disconnects/reconnects
- **Applies deadzones** (0.3) to analog sticks
- **Provides methods**:
  - `get_stick_input()` - Returns (-1 to 1, -1 to 1) for left stick
  - `get_dpad()` - Returns (up, down, left, right) booleans
  - `is_button_pressed(button)` - Check if button is held
  - `was_button_pressed(button)` - Check if button just pressed
  - `get_trigger_input()` - Returns (LT, RT) values 0-1
  - `is_connected()` - Check if gamepad is available

### Button Mapping

```python
buttons = {
    'a': 0,        # A/Cross button
    'b': 1,        # B/Circle button
    'x': 2,        # X/Square button
    'y': 3,        # Y/Triangle button
    'lb': 4,       # LB/L1 button
    'rb': 5,       # RB/R1 button
    'back': 6,     # Back/Select button
    'start': 7,    # Start button
}
```

---

## 🧪 TESTING RECOMMENDATIONS

### Test Checklist

- [ ] Connect Nintendo Switch Pro Controller
- [ ] Connect Xbox controller
- [ ] Connect PlayStation controller
- [ ] Test movement with analog stick
- [ ] Test all action buttons
- [ ] Test D-pad navigation on login screen
- [ ] Test camera recording with gamepad
- [ ] Test video upload with gamepad
- [ ] Test disconnecting and reconnecting
- [ ] Test keyboard fallback (no controller)

### Expected Behavior

1. **On Startup**: Game prints gamepad name if detected
2. **Movement**: Smooth analog stick control with deadzone
3. **Buttons**: Immediate response to button presses
4. **Fallback**: Game works perfectly with keyboard if no controller

---

## 🐛 TROUBLESHOOTING

### "No gamepad detected" but controller is plugged in

1. Check USB connection or Bluetooth pairing
2. Try a different USB port
3. Restart the game
4. Verify controller works in another game (Steam, etc.)

### Button presses not registering

1. Make sure you're not holding the button down (use quick presses)
2. Check that the game window has focus
3. Try a different controller if available

### Analog stick drifts or doesn't center

1. Increase deadzone in `GamepadHandler.__init__()` (change 0.3 to 0.4 or higher)
2. Clean the analog stick contacts
3. Try a different controller

### Works on PC but not on Switch (via emulator)

- Ensure the emulator has proper gamepad passthrough enabled
- Check emulator settings for controller support

---

## 🎮 QUICK START

```bash
# Install any required packages (already included with Pygame)
pip install pygame

# Start the game (controller optional!)
python main.py

# If controller connected:
# - Move with left stick
# - Press buttons for actions
# - Use D-pad on menus

# If no controller:
# - Use WASD for movement
# - Use function keys for actions
# - Use arrow keys for menus
```

---

## 📝 NOTES

- **All keyboard shortcuts still work** even with a controller connected
- **D-pad and analog stick are independent** - use whichever feels better
- **Deadzones prevent stick drift** - small movements won't register
- **Works on most operating systems**: Windows, macOS, Linux
- **Automatic detection** means no config files needed

---

## ✨ FEATURES SUMMARY

✅ Full gamepad support (Nintendo, Xbox, PlayStation)
✅ Analog stick movement with deadzone
✅ D-pad menu navigation
✅ All action buttons mapped
✅ Camera app full gamepad control
✅ Login screen gamepad support
✅ Automatic controller detection
✅ Reconnection support
✅ Keyboard fallback
✅ Works on Windows, Mac, Linux

---

**Enjoy your car race adventure with your favorite console controller!** 🏎️
