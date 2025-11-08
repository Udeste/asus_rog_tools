from pathlib import Path
from typing import Tuple, Dict

class FanController:
    """
    FanController class to manage custom fan curves for ASUS laptops using asus-nb-wmi driver.
    """

    def __init__(self):
        self.hwmon_path = self.__find_hwmon_path()
        self.fan_curves = self.__get_custom_fan_curves()

    def __find_hwmon_path(self) -> str | bool:
        ''' Find the hwmon path for asus_custom_fan_curve '''
        for p in Path("/sys/devices/platform/asus-nb-wmi/hwmon/").glob("hwmon*"):
            name_file = p / "name"
            if name_file.exists() and name_file.read_text().strip() == "asus_custom_fan_curve":
                return str(p)
        return False

    def __get_custom_fan_curves(self) -> Dict:
        # TODO: Add option to read custom curves from a config file
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
        return { "cpu": cpu_fan_curve, "gpu": gpu_fan_curve }

    def __apply_custom_fan_curve(self, curve: Tuple[str, ...], pwm_prefix: str):
        """
        Applies the fan curves to the hwmon interface
        This function writes the temperature and PWM values to the appropriate files.

        hwmon_path: path of the asus-nb-wmi hwmon device
        curve: list of strings in the format "temp:pwm"
        pwm_prefix: "pwm1" for CPU, "pwm2" for GPU
        """
        # TODO: extend the function to allow changing fan curves separately for CPU and GPU
        if not pwm_prefix or not curve:
            raise Exception("Invalid parameters for applying fan curves.")

        for i in range(0,8):
            step_values = curve[i].split(":")
            step_temp = step_values[0]
            step_pwm = step_values[1]
            pwm_path = f"{self.hwmon_path}/{pwm_prefix}_auto_point{i + 1}_pwm"
            temp_path = f"{self.hwmon_path}/{pwm_prefix}_auto_point{i + 1}_temp"
            with open(pwm_path, "w") as pwm_file:
                pwm_file.write(step_pwm)
            with open(temp_path, "w") as temp_file:
                temp_file.write(step_temp)

    def __enable_custom_pwm_control(self, mode="1", pwm_prefix: str = "pwm1"):
        """
        Enable custom PWM control. This is required to apply custom fan curves.
        1: Enable custom control
        2: Enable automatic control based on built-in UEFI curves
        """
        with open(f"{self.hwmon_path}/{pwm_prefix}_enable", "w") as enable_file:
            enable_file.write(mode)

    def supported_profiles(self) -> Tuple[str, ...]:
        """ Return a list of supported fan profiles """
        curves = self.__get_custom_fan_curves()
        return tuple(curves["cpu"].keys())

    def is_device_supported(self) -> bool:
        """ Check if the current device is supported by verifying the hwmon path """
        return False if not self.hwmon_path else True

    def apply_custom_fan_profile(self, profile: str) -> None:
        if not self.is_device_supported():
            raise Exception("The current device is not supported.")

        if profile not in self.supported_profiles():
            raise Exception(f"Fan profile '{profile}' is not supported.")

        curves = self.__get_custom_fan_curves()

        # Apply CPU fan curve
        self.__apply_custom_fan_curve(curves["cpu"][profile], "pwm1")
        self.__enable_custom_pwm_control(mode="1", pwm_prefix="pwm1")

        # Apply GPU fan curve
        self.__apply_custom_fan_curve(curves["gpu"][profile], "pwm2")
        self.__enable_custom_pwm_control(mode="1", pwm_prefix="pwm2")

