"""
Module `gpu_power_manager`
-------------------------

This module manages the nvidia dGPU power state in Muxless laptops, like the ASUS ROG G14 2020 model.
It can switch between two modes:
 - off: Turns off the GPU to save power.
 - on: Turns on the GPU for maximum performance.

In order to run properly, the module requires that your user has some sudo privileges without password prompt.
You need to add the following lines to your sudoers file (run 'sudo visudo
and add the lines at the end of the file):
 your_username ALL=(ALL) NOPASSWD: /usr/sbin/modprobe -r nvidia_*
 your_username ALL=(ALL) NOPASSWD: /usr/bin/pkill -f nvidia

Then you need the folowing udev rueles to allow writing to the PCI sysfs files without root privileges.
Create a file named /etc/udev/rules.d/99-nvidia-gpu.rules
with the following content, replacing <your_groupname> with your actual groupname:

 # Set permissions on NVIDIA GPU device
 SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{device}=="0x1f12", RUN+="/bin/chown root:<your_groupname> /sys%p/remove"

 # Set permissions on NVIDIA Audio device
 SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{device}=="0x10f9", RUN+="/bin/chown root:<your_groupname> /sys%p/remove"

 # Set permissions on NVIDIA USB host device
 SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{device}=="0x1ada", RUN+="/bin/chown root:<your_groupname> /sys%p/remove"

 # Set permissions on NVIDIA USB-C device
 SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{device}=="0x1adb", RUN+="/bin/chown root:<your_groupname> /sys%p/remove"
"""

from pathlib import Path
import subprocess

class GPUPowerManager:
    gpu_pci_address = "0000:01:00.0"
    audio_pci_address = "0000:01:00.1"
    usb_host_pci_address = "0000:01:00.2"
    usb_c_pci_address = "0000:01:00.3"

    def __init__(self):
        pass

    def is_gpu_attached(self) -> bool:
        """ Check if the NVIDIA GPU is attached to the PCI bus """
        gpu_path = Path(f"/sys/bus/pci/devices/{self.gpu_pci_address}")
        if gpu_path.exists():
            with open(gpu_path / "power_state", "r") as power_state_file:
                state = power_state_file.read().strip()
                if state == "D0" or state == "D3hot" or state == "D3cold":
                    return True
        return False

    def __kill_process_using_gpu(self):
        """
        Kill all processes using the NVIDIA GPU
        Add your user to the sudoers file with NOPASSWD for 'pkill -f nvidia' command to avoid password prompt.
        """
        subprocess.run(["sudo", "pkill", "-f", "nvidia"], check=False)

    def __unload_modules(self):
        """
        Unload NVIDIA kernel modules
        Add your user to the sudoers file with NOPASSWD for 'modprobe -r nvidia_*' command to avoid password prompt.
        """
        subprocess.run(["sudo", "modprobe", "-r", "nvidia_drm", "nvidia_modeset", "nvidia_uvm", "nvidia", "i2c_nvidia_gpu"], check=False)

    def __load_modules(self):
        """
        Load NVIDIA kernel modules
        This function is for later usage.
        At the moment the kernel modules are loaded automatically when the GPU is re-attached.
        """
        pass

    def __detach_nvidia_devices(self):
        """
        Detach NVIDIA devices from PCI bus
        remove the GPU, audio, USB host, and USB-C devices from the PCI bus
        """
        with open(f"/sys/bus/pci/devices/{self.gpu_pci_address}/remove", "w") as gpu_remove_file:
            gpu_remove_file.write("1\n")
        with open(f"/sys/bus/pci/devices/{self.audio_pci_address}/remove", "w") as audio_remove_file:
            audio_remove_file.write("1\n")
        with open(f"/sys/bus/pci/devices/{self.usb_host_pci_address}/remove", "w") as usb_host_remove_file:
            usb_host_remove_file.write("1\n")
        with open(f"/sys/bus/pci/devices/{self.usb_c_pci_address}/remove", "w") as usb_c_remove_file:
            usb_c_remove_file.write("1\n")

    def __attach_nvidia_devices(self):
        """ Attach NVIDIA devices to PCI bus """
        with open("/sys/bus/pci/rescan", "w") as rescan_file:
            rescan_file.write("1\n")

    def power_on(self):
        """Turn the GPU ON"""
        print("Powering ON the GPU...")
        self.__attach_nvidia_devices()
        self.__load_modules()
        print("GPU powered ON")

    def power_off(self):
        """Turn the GPU OFF"""
        print("Powering OFF the GPU...")
        print("Killing processes using the GPU...")
        self.__kill_process_using_gpu()
        print("Unloading NVIDIA kernel modules...")
        self.__unload_modules()
        print("Detaching NVIDIA devices from PCI bus...")
        self.__detach_nvidia_devices()
        print("GPU powered OFF")


