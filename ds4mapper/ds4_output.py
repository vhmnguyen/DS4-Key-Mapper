from __future__ import annotations

import hid


SONY_VENDOR_ID = 0x054C
DS4_PRODUCT_IDS = {0x05C4, 0x09CC}


class DS4Output:
    """USB lightbar and rumble output for first- and second-generation DS4 pads."""

    def __init__(self) -> None:
        self.device = None
        self.color = (48, 124, 255)
        self.small_motor = 0
        self.large_motor = 0

    def connect_usb(self) -> None:
        self.close()
        for info in hid.enumerate(SONY_VENDOR_ID, 0):
            if info["product_id"] in DS4_PRODUCT_IDS and info.get("interface_number", -1) in (-1, 0, 3):
                candidate = hid.device()
                try:
                    candidate.open_path(info["path"])
                    self.device = candidate
                    self._write()
                    return
                except OSError:
                    candidate.close()
        raise RuntimeError("No writable USB DualShock 4 HID interface was found.")

    def set_color(self, red: int, green: int, blue: int) -> None:
        self.color = (red, green, blue)
        self._write()

    def set_rumble(self, small: int, large: int) -> None:
        self.small_motor = max(0, min(255, small))
        self.large_motor = max(0, min(255, large))
        self._write()

    def _write(self) -> None:
        if not self.device:
            return
        report = [0] * 32
        report[0] = 0x05
        # DS4 USB output flags. Byte 1 enables the output fields and byte 2
        # enables lightbar/rumble updates. Without 0x04, writes can succeed
        # while the controller silently ignores both effects.
        report[1] = 0xFF
        report[2] = 0x04
        report[4] = self.small_motor
        report[5] = self.large_motor
        report[6:9] = self.color
        try:
            written = self.device.write(report)
        except OSError as exc:
            raise RuntimeError(
                "Windows could not write to the DS4. Close Steam, DS4Windows, "
                "and other controller tools, reconnect by USB, and try again."
            ) from exc
        if written <= 0:
            raise RuntimeError("The DS4 accepted no output data. Reconnect it by USB and try again.")

    def close(self) -> None:
        if self.device:
            try:
                self.set_rumble(0, 0)
                self.device.close()
            except OSError:
                pass
        self.device = None
