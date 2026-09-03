from __future__ import annotations

from dataclasses import dataclass, field
import pygame


BUTTON_INDEX = {
    0: "Cross", 1: "Circle", 2: "Square", 3: "Triangle",
    4: "Share", 5: "PS", 6: "Options", 7: "L3", 8: "R3",
    9: "L1", 10: "R1",
}


@dataclass
class ControllerState:
    buttons: set[str] = field(default_factory=set)
    lx: float = 0.0
    ly: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    l2: float = 0.0
    r2: float = 0.0


class ControllerReader:
    def __init__(self) -> None:
        pygame.init()
        pygame.joystick.init()
        self.joystick: pygame.joystick.JoystickType | None = None

    def connect(self) -> str | None:
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            self.joystick = None
            return None
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        return self.joystick.get_name()

    def read(self) -> ControllerState:
        pygame.event.pump()
        if not self.joystick or not self.joystick.get_init():
            return ControllerState()

        js = self.joystick
        pressed = {
            name for index, name in BUTTON_INDEX.items()
            if index < js.get_numbuttons() and js.get_button(index)
        }

        # SDL may expose triggers as axes or buttons depending on the driver.
        axes = [js.get_axis(i) for i in range(js.get_numaxes())]
        lx, ly = self._axis(axes, 0), self._axis(axes, 1)
        rx, ry = self._axis(axes, 2), self._axis(axes, 3)
        l2 = (self._axis(axes, 4) + 1.0) / 2.0 if len(axes) > 4 else 0.0
        r2 = (self._axis(axes, 5) + 1.0) / 2.0 if len(axes) > 5 else 0.0
        if l2 > 0.08:
            pressed.add("L2")
        if r2 > 0.08:
            pressed.add("R2")

        if js.get_numhats():
            x, y = js.get_hat(0)
            if y > 0: pressed.add("D-pad Up")
            if y < 0: pressed.add("D-pad Down")
            if x < 0: pressed.add("D-pad Left")
            if x > 0: pressed.add("D-pad Right")

        return ControllerState(pressed, lx, ly, rx, ry, l2, r2)

    @staticmethod
    def _axis(axes: list[float], index: int) -> float:
        return axes[index] if index < len(axes) else 0.0

