from __future__ import annotations

import ctypes
from ctypes import wintypes
import sys


KEYEVENTF_KEYUP = 0x0002
INPUT_KEYBOARD = 1

VK = {
    "BACKSPACE": 0x08, "TAB": 0x09, "ENTER": 0x0D, "SHIFT": 0x10,
    "CTRL": 0x11, "ALT": 0x12, "ESC": 0x1B, "SPACE": 0x20,
    "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28,
    "DELETE": 0x2E,
    **{chr(code): code for code in range(ord("A"), ord("Z") + 1)},
    **{str(number): 0x30 + number for number in range(10)},
    **{f"F{number}": 0x6F + number for number in range(1, 13)},
}


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


class KeyboardOutput:
    def __init__(self) -> None:
        self.held: set[str] = set()

    def update(self, desired: set[str]) -> None:
        for key in self.held - desired:
            self._send(key, True)
        for key in desired - self.held:
            self._send(key, False)
        self.held = set(desired)

    def release_all(self) -> None:
        self.update(set())

    @staticmethod
    def is_valid(key: str) -> bool:
        return key.upper() in VK

    @staticmethod
    def _send(key: str, key_up: bool) -> None:
        if sys.platform != "win32":
            return
        virtual_key = VK.get(key.upper())
        if virtual_key is None:
            return
        event = INPUT(type=INPUT_KEYBOARD)
        event.ki = KEYBDINPUT(virtual_key, 0, KEYEVENTF_KEYUP if key_up else 0, 0, None)
        ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))

