#!/usr/bin/python
import emulator

from emulator_controller import EmuController
from emulator_gui import EmuApp

def main():
    emu = emulator.Emulator()

    # emulator will be controlled through the EmuController interface
    app = EmuApp()
    EmuController(emu, app.frame.panel)
    app.MainLoop()


if __name__ == "__main__":
    main()
