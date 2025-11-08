from pathlib import Path
from typing import Literal, Tuple, Dict

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
        return {
            "cpu": {
                "silent":      ("30:0",   "40:10",  "50:24",  "58:36",  "66:52",  "72:68",  "78:88",  "85:105"),
                "balanced":    ("30:12",  "47:28",  "54:45",  "61:70",  "68:95",  "74:125", "80:155", "85:185"),
                "performance": ("30:18",  "47:38",  "54:60",  "61:85",  "68:115", "74:150", "80:185", "85:210"),
                "max_speed":   ("20:255", "30:255", "40:255", "50:255", "60:255", "70:255", "80:255", "90:255"),
            },
            "gpu": {
                "silent":      ("30:0",   "40:12",  "50:28",  "58:42",  "66:60",  "72:78",  "78:92",  "85:100"),
                "balanced":    ("30:12",  "47:32",  "54:50",  "61:78",  "68:105", "74:138", "80:170", "85:200"),
                "performance": ("30:20",  "47:44",  "54:70",  "61:98",  "68:130", "74:165", "80:200", "85:230"),
                "max_speed":   ("20:255", "30:255", "40:255", "50:255", "60:255", "70:255", "80:255", "90:255"),
            }
        }

    def __apply_custom_fan_curve(self, curve: Tuple[str, ...], fan: Literal["cpu", "gpu"] = "cpu"):
        """
        Applies the fan curves to the hwmon interface
        This function writes the temperature and PWM values to the appropriate files.

        curve: list of strings in the format "temp:pwm"
        fan: "cpu" or "gpu"
        """

        if not curve:
            raise Exception("Can't apply fan curve. Missing fan curve data.")

        pwm_prefix = "pwm1" if fan == "cpu" else "pwm2"

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

    def __enable_custom_pwm_control(self, mode="1", fan: Literal["cpu", "gpu"] = "cpu"):
        """
        Enable custom PWM control. This is required to apply custom fan curves.

        mode: "1" Enables custom control
        mode: "2" Enables automatic control based on built-in UEFI curves
        mode: "3" Enables automatic control based on built-in UEFI curves and reset the custom curves to the default values
        fan: "cpu" for CPU fan, "gpu" for GPU fan
        """

        fan_prefix = "pwm1" if fan == "cpu" else "pwm2"
        with open(f"{self.hwmon_path}/{fan_prefix}_enable", "w") as enable_file:
            enable_file.write(mode)

    def supported_profiles(self) -> Tuple[str, ...]:
        """ Return a list of supported fan profiles """

        curves = self.__get_custom_fan_curves()
        return tuple(curves["cpu"].keys())

    def is_device_supported(self) -> bool:
        """ Check if the current device is supported by verifying the hwmon path """

        return bool(self.hwmon_path)

    def apply_custom_fan_profile(self, profile: str, fan: Literal["cpu", "gpu", "all"] = "all") -> None:
        #TODO: Allow mode 2 and mode 3 for stock fan curves

        if not self.is_device_supported():
            raise Exception("The current device is not supported.")

        if profile not in self.supported_profiles():
            raise Exception(f"Fan profile '{profile}' is not supported.")

        curves = self.__get_custom_fan_curves()

        fans_to_change = []

        match fan:
            case "cpu":
                fans_to_change.append("cpu")
            case "gpu":
                fans_to_change.append("gpu")
            case "all":
                fans_to_change.extend(["cpu", "gpu"])

        for fan_type in fans_to_change:
            self.__apply_custom_fan_curve(curve=curves[fan_type][profile], fan=fan_type)
            self.__enable_custom_pwm_control(mode="1", fan=fan_type)

