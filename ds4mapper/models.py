from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json


DS4_BUTTONS = [
    "Cross", "Circle", "Square", "Triangle", "Share", "PS", "Options",
    "L1", "R1", "L2", "R2", "L3", "R3", "D-pad Up", "D-pad Down",
    "D-pad Left", "D-pad Right",
]


@dataclass
class Profile:
    name: str = "Default"
    mode: str = "keyboard"
    mappings: dict[str, str] = field(default_factory=lambda: {
        "Cross": "SPACE", "Circle": "ESC", "Square": "E", "Triangle": "Q",
        "D-pad Up": "UP", "D-pad Down": "DOWN", "D-pad Left": "LEFT",
        "D-pad Right": "RIGHT", "L1": "SHIFT", "R1": "CTRL",
        "Options": "ENTER", "Share": "TAB",
    })
    deadzone: float = 0.15
    lightbar: str = "#307CFF"

    @classmethod
    def load(cls, path: Path) -> "Profile":
        return cls(**json.loads(path.read_text(encoding="utf-8")))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


XBOX_PRESET = Profile(
    name="Xbox 360 Preset",
    mode="xbox",
    mappings={
        "Cross": "A", "Circle": "B", "Square": "X", "Triangle": "Y",
        "L1": "LB", "R1": "RB", "L2": "LT", "R2": "RT",
        "L3": "LS", "R3": "RS", "Share": "BACK", "Options": "START",
        "PS": "GUIDE", "D-pad Up": "DPAD_UP", "D-pad Down": "DPAD_DOWN",
        "D-pad Left": "DPAD_LEFT", "D-pad Right": "DPAD_RIGHT",
    },
)

