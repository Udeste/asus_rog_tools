#!/usr/bin/env python3
#
# This script creates a system tray icon to show and control the GPU power state.
#
# It requires PyQt5 to be installed.
# For fedora: sudo dnf install python3-qt5
#
# It also requires the existence of the script ./gpu-mode, and the icons gpu-on, gpu-off and gpu-detached to be available in the system theme.
# Usually the icons can be placed under ~/.local/share/icons/
#
# The script should be run in background, for example by adding it to the startup applications.
# For instance in KDE you can add from System Settings -> Startup and Shutdown -> Autostart -> Add Script...
#

import sys
from modules.gpu_power_manager import GPUPowerManager
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

gpu_manager = GPUPowerManager()

def run_gpu_mode(mode):
    match mode:
        case "on":
            gpu_manager.power_on()
        case "off":
            gpu_manager.power_off()

app = QApplication(sys.argv)
tray = QSystemTrayIcon()
tray.setIcon(QIcon.fromTheme("gpu-on"))
tray.setToolTip("GPU Mode")

menu = QMenu()

perf_action = QAction("Turn ON")
perf_action.triggered.connect(lambda: run_gpu_mode("on"))
menu.addAction(perf_action)

battery_action = QAction("Turn OFF")
battery_action.triggered.connect(lambda: run_gpu_mode("off"))
menu.addAction(battery_action)

# auto_action = QAction("Auto")
# auto_action.triggered.connect(lambda: run_gpu_mode("auto"))
# menu.addAction(auto_action)
exit_action = QAction("Exit")
exit_action.triggered.connect(lambda: sys.exit())
menu.addAction(exit_action)

tray.setContextMenu(menu)
tray.show()

# Update icon every 10 seconds
def update_icon():
    state = gpu_manager.is_gpu_attached()
    match state:
        # case False:
        #     tray.setToolTip("GPU OFF (suspended)")
        #     tray.setIcon(QIcon.fromTheme("gpu-off"))
        case True:
            tray.setIcon(QIcon.fromTheme("gpu-on"))
            tray.setToolTip("GPU ON")
        case False:
            tray.setToolTip("GPU OFF (detached)")
            tray.setIcon(QIcon.fromTheme("gpu-detached"))

timer = QTimer()
timer.timeout.connect(update_icon)
timer.start(10000)  # 10 seconds
update_icon()

sys.exit(app.exec_())
