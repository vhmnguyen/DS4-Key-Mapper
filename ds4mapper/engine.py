from __future__ import annotations

from .input_device import ControllerReader, ControllerState
from .keyboard_output import KeyboardOutput
from .models import Profile
from .xbox_output import XboxOutput


class MappingEngine:
    def __init__(self) -> None:
        self.reader = ControllerReader()
        self.keyboard = KeyboardOutput()
        self.xbox = XboxOutput()
        self.profile = Profile()
        self.running = False
        self.last_state = ControllerState()

    def connect(self) -> str | None:
        return self.reader.connect()

    def tick(self) -> ControllerState:
        state = self.reader.read()
        self.last_state = state
        if not self.running:
            return state
        if self.profile.mode == "xbox":
            self.keyboard.release_all()
            self.xbox.update(state)
        else:
            desired = {
                self.profile.mappings[button]
                for button in state.buttons
                if button in self.profile.mappings and self.profile.mappings[button]
            }
            self.keyboard.update(desired)
        return state

    def stop(self) -> None:
        self.running = False
        self.keyboard.release_all()
        self.xbox.disconnect()

