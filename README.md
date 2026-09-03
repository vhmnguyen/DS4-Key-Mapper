# DS4 Key Mapper

A Windows desktop application that maps a DualShock 4 controller to keyboard keys or an emulated Xbox 360 controller. It also includes profile saving, a live input display, USB lightbar colors, and vibration tests.

Current version: **0.1.1**

## Requirements

- Windows 10 or 11
- Python 3.11 or newer
- A DualShock 4 connected by USB or Bluetooth
- For Xbox mode: the ViGEmBus driver

## Quick start

1. Connect the controller to Windows.
2. Double-click `run.bat`. The first launch creates a virtual environment and installs dependencies.
3. Click **Connect**.
4. Select keyboard mappings or click **Xbox preset**.
5. Click **Start mapping**.

To create a standalone Windows build, run `build.bat`. The executable will appear under `dist\DS4KeyMapper`.

If Windows reports that neither `py` nor `python` is recognized, install Python from [python.org](https://www.python.org/downloads/windows/) and enable **Add python.exe to PATH** in the installer. Close and reopen the terminal afterward.

## Xbox 360 mode

Xbox mode uses the `vgamepad` Python package, which communicates with ViGEmBus. Install the ViGEmBus driver before starting Xbox mode. ViGEmBus is retired upstream, so this app isolates it in `ds4mapper/xbox_output.py`, allowing a future virtual-controller backend to replace it.

Windows may see both the real DS4 and virtual Xbox controller. If a game responds twice, install and configure HidHide so the game only sees the virtual controller. Make sure this mapper remains allowed to read the physical DS4.

## Lightbar and vibration

These features currently use direct DS4 USB HID output. Connect by USB, open the **Lightbar & vibration** tab, and click **Connect effects**. Bluetooth HID output uses a different report format and is not enabled in this first version.

If input works but effects do not, completely exit Steam, DS4Windows, reWASD, and other controller software, then unplug and reconnect the DS4 by USB. Another program can retain control of the output interface even while this app can still read buttons.

## Notes

- Keyboard output uses the Windows `SendInput` API.
- If a game runs as administrator, this app may also need to run as administrator.
- The first detected controller is used.
- SDL controller layouts can vary by driver. The live input panel makes incorrect button assignments visible.
- Keep an ordinary keyboard available while testing new mappings.

## Project structure

- `main.py`: entry point
- `ds4mapper/app.py`: Tkinter user interface
- `ds4mapper/input_device.py`: controller input through pygame/SDL
- `ds4mapper/engine.py`: mapping loop
- `ds4mapper/keyboard_output.py`: Windows keyboard output
- `ds4mapper/xbox_output.py`: virtual Xbox output
- `ds4mapper/ds4_output.py`: USB lightbar and vibration output
- `profiles/default.json`: example profile

## Current limitations

- Windows only
- One controller at a time
- Xbox output depends on ViGEmBus
- Lightbar and vibration output are USB-only
- No mouse mapping, macros, touchpad, gyro, or automatic per-game profiles yet
