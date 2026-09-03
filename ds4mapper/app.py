from __future__ import annotations

import copy
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

from .ds4_output import DS4Output
from .engine import MappingEngine
from .keyboard_output import VK
from .models import DS4_BUTTONS, Profile, XBOX_PRESET


class MapperApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("DS4 Key Mapper")
        self.geometry("900x680")
        self.minsize(760, 560)
        self.configure(bg="#10131a")
        self.engine = MappingEngine()
        self.ds4_output = DS4Output()
        self.profile = Profile()
        self.mapping_vars: dict[str, tk.StringVar] = {}
        self.status = tk.StringVar(value="Controller not connected")
        self.live = tk.StringVar(value="Pressed: —")
        self.mode = tk.StringVar(value="keyboard")
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(16, self._poll)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#10131a")
        style.configure("Card.TFrame", background="#1a1f2b")
        style.configure("TLabel", background="#10131a", foreground="#e9eef7", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 24), foreground="#ffffff")
        style.configure("Card.TLabel", background="#1a1f2b", foreground="#e9eef7")
        style.configure("TButton", padding=(12, 7))

        outer = ttk.Frame(self, padding=22)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="DS4 Key Mapper", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Turn a DualShock 4 into keyboard controls or an Xbox 360 controller.").pack(anchor="w", pady=(2, 16))

        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(toolbar, text="Connect", command=self._connect).pack(side="left")
        self.run_button = ttk.Button(toolbar, text="Start mapping", command=self._toggle)
        self.run_button.pack(side="left", padx=8)
        ttk.Button(toolbar, text="Xbox preset", command=self._xbox_preset).pack(side="left")
        ttk.Button(toolbar, text="Save profile", command=self._save).pack(side="right")
        ttk.Button(toolbar, text="Load profile", command=self._load).pack(side="right", padx=8)

        info = ttk.Frame(outer, style="Card.TFrame", padding=14)
        info.pack(fill="x", pady=(0, 14))
        ttk.Label(info, textvariable=self.status, style="Card.TLabel").pack(anchor="w")
        ttk.Label(info, textvariable=self.live, style="Card.TLabel").pack(anchor="w", pady=(5, 0))

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        mapping = ttk.Frame(notebook, padding=14)
        effects = ttk.Frame(notebook, padding=14)
        notebook.add(mapping, text="Mappings")
        notebook.add(effects, text="Lightbar & vibration")

        mode_bar = ttk.Frame(mapping)
        mode_bar.pack(fill="x", pady=(0, 10))
        ttk.Label(mode_bar, text="Output mode:").pack(side="left")
        ttk.Radiobutton(mode_bar, text="Keyboard", variable=self.mode, value="keyboard", command=self._mode_changed).pack(side="left", padx=10)
        ttk.Radiobutton(mode_bar, text="Xbox 360", variable=self.mode, value="xbox", command=self._mode_changed).pack(side="left")

        canvas = tk.Canvas(mapping, bg="#10131a", highlightthickness=0)
        scroll = ttk.Scrollbar(mapping, orient="vertical", command=canvas.yview)
        rows = ttk.Frame(canvas)
        rows.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=rows, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        keys = sorted(VK)
        for index, button in enumerate(DS4_BUTTONS):
            ttk.Label(rows, text=button, width=18).grid(row=index, column=0, sticky="w", pady=4)
            var = tk.StringVar(value=self.profile.mappings.get(button, ""))
            self.mapping_vars[button] = var
            ttk.Combobox(rows, textvariable=var, values=[""] + keys, width=20).grid(row=index, column=1, sticky="w", padx=8)

        ttk.Label(effects, text="USB connection is required for reliable DS4 output.").pack(anchor="w", pady=(0, 15))
        ttk.Button(effects, text="Connect effects", command=self._connect_effects).pack(anchor="w")
        ttk.Button(effects, text="Choose lightbar color", command=self._choose_color).pack(anchor="w", pady=10)
        rumble = ttk.Frame(effects)
        rumble.pack(anchor="w", pady=4)
        ttk.Button(rumble, text="Test soft rumble", command=lambda: self._rumble(70, 20)).pack(side="left")
        ttk.Button(rumble, text="Test strong rumble", command=lambda: self._rumble(30, 220)).pack(side="left", padx=8)
        ttk.Button(rumble, text="Stop rumble", command=lambda: self._rumble(0, 0)).pack(side="left")

    def _connect(self) -> None:
        name = self.engine.connect()
        self.status.set(f"Connected: {name}" if name else "No controller found — plug it in and try again")

    def _toggle(self) -> None:
        if self.engine.running:
            self.engine.stop()
            self.run_button.configure(text="Start mapping")
            self.status.set("Mapping stopped")
            return
        self._apply_profile()
        try:
            if self.profile.mode == "xbox":
                self.engine.xbox.connect()
            self.engine.running = True
            self.run_button.configure(text="Stop mapping")
            self.status.set(f"Mapping active: {self.profile.mode} mode")
        except RuntimeError as exc:
            messagebox.showerror("Could not start", str(exc))

    def _apply_profile(self) -> None:
        self.profile.mode = self.mode.get()
        self.profile.mappings = {button: var.get().upper() for button, var in self.mapping_vars.items() if var.get()}
        self.engine.profile = self.profile

    def _mode_changed(self) -> None:
        self.profile.mode = self.mode.get()

    def _xbox_preset(self) -> None:
        self.profile = copy.deepcopy(XBOX_PRESET)
        self.mode.set("xbox")
        for button, var in self.mapping_vars.items():
            var.set(self.profile.mappings.get(button, ""))
        self.status.set("Xbox 360 preset loaded")

    def _save(self) -> None:
        self._apply_profile()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON profile", "*.json")])
        if path:
            self.profile.save(Path(path))
            self.status.set(f"Saved profile: {Path(path).name}")

    def _load(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON profile", "*.json")])
        if not path:
            return
        try:
            self.profile = Profile.load(Path(path))
            self.mode.set(self.profile.mode)
            for button, var in self.mapping_vars.items():
                var.set(self.profile.mappings.get(button, ""))
            self.engine.profile = self.profile
            self.status.set(f"Loaded profile: {Path(path).name}")
        except (OSError, ValueError, TypeError) as exc:
            messagebox.showerror("Invalid profile", str(exc))

    def _connect_effects(self) -> None:
        try:
            self.ds4_output.connect_usb()
            self.status.set("DS4 lightbar and vibration connected")
        except RuntimeError as exc:
            messagebox.showerror("Effects unavailable", str(exc))

    def _choose_color(self) -> None:
        chosen = colorchooser.askcolor(color=self.profile.lightbar, title="Choose lightbar color")
        if not chosen[0]:
            return
        red, green, blue = (round(value) for value in chosen[0])
        self.profile.lightbar = chosen[1]
        self.ds4_output.set_color(red, green, blue)

    def _rumble(self, small: int, large: int) -> None:
        if not self.ds4_output.device:
            messagebox.showinfo("Connect first", "Connect the controller under Lightbar & vibration first.")
            return
        self.ds4_output.set_rumble(small, large)
        if small or large:
            self.after(800, lambda: self.ds4_output.set_rumble(0, 0))

    def _poll(self) -> None:
        try:
            state = self.engine.tick()
            text = ", ".join(sorted(state.buttons)) or "—"
            self.live.set(f"Pressed: {text}    Left stick: ({state.lx:+.2f}, {state.ly:+.2f})")
        except Exception as exc:
            self.engine.stop()
            self.run_button.configure(text="Start mapping")
            self.status.set(f"Mapping stopped: {exc}")
        self.after(16, self._poll)

    def _close(self) -> None:
        self.engine.stop()
        self.ds4_output.close()
        self.destroy()


def main() -> None:
    MapperApp().mainloop()

