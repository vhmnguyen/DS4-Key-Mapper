from __future__ import annotations

from .input_device import ControllerState


class XboxOutput:
    def __init__(self) -> None:
        self.gamepad = None
        self.vg = None

    def connect(self) -> None:
        try:
            import vgamepad as vg
            self.vg = vg
            self.gamepad = vg.VX360Gamepad()
        except Exception as exc:
            raise RuntimeError(
                "Xbox emulation needs vgamepad and the ViGEmBus driver. "
                "Install both, then restart the app."
            ) from exc

    def disconnect(self) -> None:
        if self.gamepad:
            self.gamepad.reset()
            self.gamepad.update()
        self.gamepad = None

    def update(self, state: ControllerState) -> None:
        if not self.gamepad:
            self.connect()
        vg, pad = self.vg, self.gamepad
        pad.reset()
        names = {
            "Cross": "XUSB_GAMEPAD_A", "Circle": "XUSB_GAMEPAD_B",
            "Square": "XUSB_GAMEPAD_X", "Triangle": "XUSB_GAMEPAD_Y",
            "L1": "XUSB_GAMEPAD_LEFT_SHOULDER", "R1": "XUSB_GAMEPAD_RIGHT_SHOULDER",
            "L3": "XUSB_GAMEPAD_LEFT_THUMB", "R3": "XUSB_GAMEPAD_RIGHT_THUMB",
            "Share": "XUSB_GAMEPAD_BACK", "Options": "XUSB_GAMEPAD_START",
            "D-pad Up": "XUSB_GAMEPAD_DPAD_UP", "D-pad Down": "XUSB_GAMEPAD_DPAD_DOWN",
            "D-pad Left": "XUSB_GAMEPAD_DPAD_LEFT", "D-pad Right": "XUSB_GAMEPAD_DPAD_RIGHT",
        }
        for source, enum_name in names.items():
            if source in state.buttons:
                pad.press_button(button=getattr(vg.XUSB_BUTTON, enum_name))
        pad.left_joystick_float(x_value_float=state.lx, y_value_float=-state.ly)
        pad.right_joystick_float(x_value_float=state.rx, y_value_float=-state.ry)
        pad.left_trigger_float(value_float=state.l2)
        pad.right_trigger_float(value_float=state.r2)
        pad.update()

