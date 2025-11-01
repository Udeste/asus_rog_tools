#!/usr/bin/env python3
#
# This script creates a system tray icon to show and control the GPU power state.
#
# It requires PyQt5 to be installed.
# For fedora: sudo dnf install python3-qt5
#
# It also requires the existence of the script ./gpu_mode, and the icons nvidia-on and nvidia-off to be available in the system theme.
# Usually the icons can be placed under ~/.local/share/icons/
#
# The script should be run in background, for example by adding it to the startup applications.
# For instance in KDE you can add from System Settings -> Startup and Shutdown -> Autostart -> Add Script...
#

import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

PCI = "0000:01:00.0"

def get_gpu_state():
    try:
        with open(f"/sys/bus/pci/devices/{PCI}/power_state", "r") as f:
            state = f.read().strip()
            return "ON" if state == "D0" else "OFF"
    except:
        return "UNKNOWN"

def run_gpu_mode(mode):
    os.system(f"./gpu_mode {mode}")

app = QApplication(sys.argv)
tray = QSystemTrayIcon()
tray.setIcon(QIcon.fromTheme("nvidia-on"))
tray.setToolTip("GPU Mode")

menu = QMenu()

perf_action = QAction("Turn ON")
perf_action.triggered.connect(lambda: run_gpu_mode("on"))
menu.addAction(perf_action)

battery_action = QAction("Turn OFF")
battery_action.triggered.connect(lambda: run_gpu_mode("off"))
menu.addAction(battery_action)

auto_action = QAction("Auto")
auto_action.triggered.connect(lambda: run_gpu_mode("auto"))
menu.addAction(auto_action)

tray.setContextMenu(menu)
tray.show()

# Update icon every 10 seconds
def update_icon():
    state = get_gpu_state()
    if state == "ON":
        tray.setIcon(QIcon.fromTheme("nvidia-on"))
        tray.setToolTip("GPU ON")
    elif state == "OFF":
        tray.setIcon(QIcon.fromTheme("nvidia-off"))
        tray.setToolTip("GPU OFF")
    else:
        tray.setIcon(QIcon.fromTheme("dialog-warning"))
        tray.setToolTip("GPU UNKNOWN")

timer = QTimer()
timer.timeout.connect(update_icon)
timer.start(10000)  # 10 seconds
update_icon()

sys.exit(app.exec_())
