#!/usr/bin/env python3

import sys
from modules.gpu_power_manager import GPUPowerManager

def __main__():
    if len(sys.argv) != 2 or sys.argv[1] not in ["on", "off"]:
        print(f"Usage: {sys.argv[0]} [on|off]")
        sys.exit(1)

    manager = GPUPowerManager()
    match sys.argv[1]:
        case "on":
            if not manager.is_gpu_attached():
                manager.power_on()
            else:
                sys.exit("GPU is already ON")
        case "off":
            if manager.is_gpu_attached():
                manager.power_off()
            else:
                sys.exit("GPU is already OFF")

if __name__ == "__main__":
    __main__()
