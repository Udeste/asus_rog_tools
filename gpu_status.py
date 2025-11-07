#!/usr/bin/env python3
# This script checks the power state of the NVIDIA GPU and outputs whether it is ON, OFF or detached from the pci bus.

# The PCI address of the NVIDIA GPU
pci_address = "0000:01:00.0"
# The path to the power state file for the GPU
gpu_power_state_path = f"/sys/bus/pci/devices/{pci_address}/power_state"

def read_gpu_power_state():
    """
    Reads the power state of the NVIDIA GPU.
    Returns:
        0 if the GPU is suspended (D3cold)
        1 if the GPU is active (D0)
        -1 if the GPU is detached or an error occurs
    """
    try:
        with open(gpu_power_state_path, "r") as power_state_file:
            state = power_state_file.read().strip()
            match state:
                case "D3cold":
                    return 0
                case "D0":
                    return 1
    except:
        return -1

def __main__():
    state = read_gpu_power_state()
    match state:
        case 0:
            print("GPU suspended (OFF)")
        case 1:
            print("GPU active (ON)")
        case -1:
            print("GPU detached (OFF)")

if __name__ == "__main__":
    __main__()

