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

from pathlib import Path
import sys

# TODO: Add option to read custom curves from a config file
# TODO: extend the script to allow changing fan curves separately for CPU and GPU

# Format: "temp:pwm"
cpu_fan_curve = {
    "silent":      ("40:10",  "47:18",  "54:30",  "61:45",  "68:65",  "74:85",  "80:110", "85:135"),
    "balanced":    ("40:12",  "47:28",  "54:45",  "61:70",  "68:95",  "74:125", "80:155", "85:185"),
    "performance": ("40:18",  "47:38",  "54:60",  "61:85",  "68:115", "74:150", "80:185", "85:210"),
    "max_speed":   ("40:255", "47:255", "54:255", "61:255", "68:255", "74:255", "80:255", "85:255"),
}

gpu_fan_curve = {
    "silent":      ("40:10",  "47:22",  "54:36",  "61:52",  "68:72",  "74:92",  "80:115", "85:140"),
    "balanced":    ("40:12",  "47:32",  "54:50",  "61:78",  "68:105", "74:138", "80:170", "85:200"),
    "performance": ("40:20",  "47:44",  "54:70",  "61:98",  "68:130", "74:165", "80:200", "85:230"),
    "max_speed":   ("40:255", "47:255", "54:255", "61:255", "68:255", "74:255", "80:255", "85:255"),
}

supported_cpu_profiles = tuple(cpu_fan_curve.keys())
supported_gpu_profiles = tuple(gpu_fan_curve.keys())

# TODO: remove when the script supports different profiles for CPU and GPU
supported_profiles = (set(supported_cpu_profiles) & set(supported_gpu_profiles))

def get_hwmon_path():
    ''' Find the hwmon path for asus_custom_fan_curve '''
    for p in Path("/sys/devices/platform/asus-nb-wmi/hwmon/").glob("hwmon*"):
        name_file = p / "name"
        if name_file.exists() and name_file.read_text().strip() == "asus_custom_fan_curve":
            return str(p)

def apply_fan_curves(hwmon_path, curve, pwm_prefix=None):
    """
    Applies the fan curves to the hwmon interface
    This function writes the temperature and PWM values to the appropriate files.

    hwmon_path: path of the asus-nb-wmi hwmon device
    curve: list of strings in the format "temp:pwm"
    pwm_prefix: "pwm1" for CPU, "pwm2" for GPU
    """
    if not pwm_prefix or not hwmon_path or not curve:
        sys.exit("Invalid parameters for applying fan curves.")

    for i in range(0,8):
        step_values = curve[i].split(":")
        step_temp = step_values[0]
        step_pwm = step_values[1]
        pwm_path = f"{hwmon_path}/{pwm_prefix}_auto_point{i + 1}_pwm"
        temp_path = f"{hwmon_path}/{pwm_prefix}_auto_point{i + 1}_temp"
        with open(pwm_path, "w") as pwm_file:
            pwm_file.write(step_pwm)
        with open(temp_path, "w") as temp_file:
            temp_file.write(step_temp)

def enable_custom_pwm_control(hwmon_path, mode="1", pwm_prefix=None):
    """
    Enable custom PWM control. This is required to apply custom fan curves.
    1: Enable custom control
    2: Enable automatic control based on built-in UEFI curves
    """
    with open(f"{hwmon_path}/{pwm_prefix}_enable", "w") as enable_file:
        enable_file.write(mode)

# Main function
def __main__():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: fan-control {supported_profiles}")

    profile = sys.argv[1]
    hwmon_path = get_hwmon_path()

    if profile not in supported_profiles:
        sys.exit(f"Currently supported profiles are: {supported_profiles}")

    if not hwmon_path:
        sys.exit("No compatible device found. Exiting...")

    print(f"Found device at {hwmon_path}")

    try:
        cpu_curve = cpu_fan_curve[profile]
        gpu_curve = gpu_fan_curve[profile]

        apply_fan_curves(hwmon_path, cpu_curve, pwm_prefix="pwm1")
        apply_fan_curves(hwmon_path, gpu_curve, pwm_prefix="pwm2")

        enable_custom_pwm_control(hwmon_path, mode="1", pwm_prefix="pwm1")
        enable_custom_pwm_control(hwmon_path, mode="1", pwm_prefix="pwm2")
    except:
        sys.exit("Failed to apply fan curves. Make sure you have the required permissions.")


if __name__ == "__main__":
    __main__()

