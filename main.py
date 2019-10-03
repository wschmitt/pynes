#!/usr/bin/python
import emulator
import rom as Rom

from emulator_controller import EmuController
from emulator_gui import EmuApp


def main():
    # emulator will be controlled through the EmuController interface
    sim = emulator.Emulator()

    app = EmuApp()
    EmuController(sim, app.frame.panel)

    app.MainLoop()


if __name__ == "__main__":
    main()
