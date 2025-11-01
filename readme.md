This repository contains a collection of tools and scripts designed to manage peripherals on Linux on ASUS ROG (Republic of Gamers) laptops.

The target is the ROG Zephyrus G14, 2020 model (GA401IV) but some of the tools may work on other ASUS ROG models as well.

It contains the following tools:
- [fan-control](./fan-control): A script that manages the CPU and GPU fan speeds through the `asus-nb-wmi` kernel module, that exposes a custom fan curve feature based on temperatures and PWM.
- [gpu-mode](./gpu-mode): A script to control the discrete GPU (nvidia) power state. On Muxless models (like the GA401IV), it allows seamlessly turn on or off the dGPU without rebooting or restarting the session. This is useful to save power when the dGPU is not needed.
- [gpu-tray](./gpu-tray.py): A system tray application that shows the power status of the discrete GPU and allows to toggle it on or off with a single click. It uses the `gpu-mode` script under the hood.

