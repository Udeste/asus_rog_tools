#!/usr/bin/env python3

#
# Fan control script for ASUS laptops using asus-nb-wmi driver
#
# Usage: fan-control {silent|balanced|performance}
#
# It sets predefined fan speed curves for CPU and GPU based on the selected mode.
# It requires write permissions to the hwmon interface, which may need sudo privileges or appropriate rules to allow non-root access.
#
# The privileges can be granted with an /etc/tmpfiles.d/asus_fan_perms.conf with the following content:
#
# PWM1 and PWM2 auto points and temp files (any hwmon*)
# z /sys/devices/platform/asus-nb-wmi/hwmon/hwmon*/pwm*_auto_point*_pwm 664 root yourusername - -
# z /sys/devices/platform/asus-nb-wmi/hwmon/hwmon*/pwm*_auto_point*_temp 664 root yourusername - -

# PWM1 and PWM2 enable files
# z /sys/devices/platform/asus-nb-wmi/hwmon/hwmon*/pwm*_enable 664 root yourusername - -

import sys
from modules.fan_controller import FanController

# Main function
def __main__():
    fan_controller = FanController()

    if len(sys.argv) != 2:
        sys.exit(f"Usage: fan-control {fan_controller.supported_profiles()}")

    profile = sys.argv[1]
    try:
        fan_controller.apply_custom_fan_profile(profile)
        print(f"Applied '{profile}' fan profile successfully.")
    except Exception as e:
        sys.exit("Failed to apply fan curves. Error: " + str(e))

if __name__ == "__main__":
    __main__()

