# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""
Author: Werner Kaul-Gothe
Department: VPT
Organisation: Universität der Künste Berlin IAS
Date: 2025-02-19

Description:
This module provides backend functionality for the PS-280 Climate Control Editor by PIKK-Systems.
It enables loading, editing, and saving TOML configuration files, integrating MQTT topics,
managing firmware, and generating labels.

Dependencies:
    - os: File system operations
    - sys: System operations
    - time: Time-based operations
    - subprocess: Execute system commands
    - platform: Detect operating system
    - webbrowser: Open web pages
    - PIL (Pillow): Image processing
    - toml: Handle TOML configuration files
    - yaml: Handle YAML configuration files
    - logging: Logging operations

"""

import os
import sys
import time
import subprocess
import platform
import webbrowser
import logging
import yaml
from PIL import Image
import toml

## Define the toolbox root path and ensure it's in sys.path
#TOOLBOXROOT = os.path.join(os.path.abspath("../.."), 'src')
#if TOOLBOXROOT not in sys.path:
#    sys.path = [TOOLBOXROOT] + sys.path

from .ps280_toolbox import PS280#, flash_firmware, configure_for_udk

from .stickertool import Sticker
# Define standard output and error streams
stdoutstream = sys.stdout
stderrstream = sys.stderr

def is_macos() -> bool:
    """
    Check if the current operating system is macOS.
    
    Returns:
        bool: True if the system is macOS, False otherwise.
    """
    return platform.system() == "Darwin"

def remove_package_attribute(folder_path: str):
    """
    Remove the 'com.apple.package-type' attribute from a folder on macOS.
    
    Args:
        folder_path (str): The path of the folder.
    
    Raises:
        FileNotFoundError: If the folder does not exist.
    """
    if not is_macos():
        print("This script can only be executed on macOS.")
        return
    
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' was not found.")
    
    try:
        subprocess.run(
            ["xattr", "-d", "com.apple.package-type", folder_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Successfully removed the 'com.apple.package-type' attribute.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing attribute: {e.stderr.strip()}")

def split_path(path: str):
    """
    Split a file path into its components.
    
    Args:
        path (str): The file path to split.
    
    Returns:
        list: A list of path components.
    """
    components = []
    while True:
        path, tail = os.path.split(path)
        if tail:
            components.insert(0, tail)
        else:
            if path:
                components.insert(0, path)
            break
    return components

def add_ps280_extensions(path: str) -> str:
    """
    Append the '.ps280' extension to each component in a file path.
    
    Args:
        path (str): The original file path.
    
    Returns:
        str: The modified file path with '.ps280' extensions.
    """
    components = split_path(path)
    return os.path.join(*[f"{p}.ps280" for p in components])

def strip_ps280_extensions(path: str) -> str:
    """
    Remove the '.ps280' extension from each component in a file path.
    
    Args:
        path (str): The file path with '.ps280' extensions.
    
    Returns:
        str: The cleaned file path without '.ps280' extensions.
    """
    components = split_path(path)
    return os.path.join(*[p.rstrip(".ps280") for p in components])


class PS280EditorBackend:
    """
    Backend logic for the PS-280 Climate Control Editor.
    Manages configuration files, MQTT topics, firmware handling, and template management.
    """
    
    def __init__(self, database_root, firmware_dir, template_dir,
                 sticker_config_file, sticker_template_file,
                 topic_upload="MQTT.TOPIC_UP", topic_download="MQTT.TOPIC_DOWN", 
                 topic_client_id="MQTT.CLIENT_ID",
                 topic_serial="CORE.SERIAL", topic_version="CORE.VERSION",
                 topic_broker_ip="HUB.REMOTE_IP", parameters_ignore=[],
                 parameters_superuser=[]):
        """
        Initialize the backend with file paths and MQTT configuration settings.
        
        Args:
            database_root (str): Root path for database storage.
            firmware_dir (str): Directory containing firmware files.
            template_dir (str): Directory containing configuration templates.
            sticker_config_file (str): Path to the sticker configuration file.
            sticker_template_file (str): Path to the sticker template file.
            topic_upload (str): MQTT topic for uploading configurations.
            topic_download (str): MQTT topic for downloading configurations.
            topic_serial (str): MQTT topic for serial communication.
            topic_version (str): MQTT topic for firmware versioning.
            topic_broker_ip (str): MQTT broker IP configuration topic.
            parameters_ignore (list): List of ignored parameters.
            parameters_superuser (list): List of superuser parameters.
        """
        self.database_root = database_root
        self.firmware_dir = firmware_dir
        self.template_dir = template_dir
        self.sticker_template_file = sticker_template_file
        self.sticker_config_file = sticker_config_file
        self.current_file_path = ""
        self.toml_data = {}
        self.temp_toml_data = {}
        self.topic_upload = topic_upload
        self.topic_download = topic_download
        self.topic_serial = topic_serial
        self.topic_client_id = topic_client_id
        self.topic_version = topic_version
        self.topic_broker_ip = topic_broker_ip
        self.parameters_ignore = parameters_ignore
        self.parameters_superuser = parameters_superuser
        self.firmware = {'version': '', 'bootloader': '', 'partitiontable': '', 'firmwarebin': ''}
        self.cfg_template = None
        self.PS280 = None
        self.data = None
        self.success = False

    @property
    def path_as_topic(self):
        """
        Returns the current file path as an MQTT topic format.
        """
        return os.path.dirname(self.current_file_path).split(self.database_root)[-1].strip('/\\')

    @property
    def database_name(self):
        """
        Returns the name of the database.
        """
        return os.path.basename(self.database_root)

    def load_toml_file(self, file_path):
        """
        Loads a TOML configuration file into memory.
        
        Args:
            file_path (str): Path to the TOML file.
        
        Returns:
            tuple: (bool, str) indicating success and message.
        """
        try:
            with open(file_path, "r") as file:
                self.toml_data = toml.load(file)
            self.current_file_path = file_path
            return True, "File loaded successfully!"
        except Exception as e:
            return False, f"Error loading file: {e}"

    def save_toml_file(self):
        """
        Saves the current TOML configuration to a file.
        
        Returns:
            tuple: (bool, str) indicating success and message.
        """
        if self.current_file_path:
            try:
                targetpath = os.path.dirname(os.path.join(self.current_file_path))
                os.makedirs(targetpath, exist_ok=True)
                with open(os.path.join(self.current_file_path), "w") as file:
                    toml.dump(self.toml_data, file)
                return True, "File saved successfully!"
            except Exception as e:
                return False, f"Error saving file: {e}"
        return False, "No file selected!"

    def update_configuration_from_template(self, templatefile):
        """
        Load a configuration template and update the current configuration.
        
        Args:
            templatefile (str): Name of the template file.
        
        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            with open(os.path.join(self.template_dir, templatefile), "r") as file:
                self.template_data = toml.load(file)
        except Exception as e:
            print(f"Error loading template {templatefile}:\n{e}", file=sys.stderr)
            return False
        
        errors_occurred = False
        for section in self.template_data:
            for row in self.template_data[section]:
                try:
                    if self.toml_data[section][row] != self.template_data[section][row]:
                        print(f"Updating {section}.{row} from {self.toml_data[section][row]} to {self.template_data[section][row]}")
                    else:
                        print(f"Keeping {section}.{row} at {self.toml_data[section][row]}")
                    self.update_toml_data(section, row, self.template_data[section][row])
                except Exception as e:
                    print(f"Error updating {section}.{row}:\n{e}")
                    errors_occurred = True
        
        if errors_occurred:
            print(f"Configuration update from template {templatefile} completed with errors!", file=sys.stderr)
        else:
            print(f"Configuration update from template {templatefile} successfully completed!")
        return True

    def set_file_path_to_topic(self):
        """
        Set the file path based on the MQTT topic.
        
        Returns:
            str: The updated file path.
        """
        section, key = self.topic_upload.split(".")
        try:
            path = add_ps280_extensions(self.toml_data[section][key])
            self.current_file_path = os.path.join(self.database_root, path, "config.toml")
            return f"Current file path set: {self.current_file_path}"
        except Exception as e:
            return False, f"Error setting file path: {e}"
    
    def set_configuration_topics(self, topic):
        """
        Set the MQTT configuration topics.
        
        Args:
            topic (str): The MQTT topic to set.
        
        Returns:
            tuple: (bool, str) Success status and message.
        """
        u_section, u_key = self.topic_upload.split(".")
        d_section, d_key = self.topic_download.split(".")
        try:
            self.toml_data[u_section][u_key] = topic
            self.toml_data[d_section][d_key] = f'{topic}/dl'
            return True, f"Configuration topics set to: {topic}"
        except Exception as e:
            return False, f"Error setting configuration topics: {e}"
    
    def set_configuration_serial(self, serial):
        """
        Set the configuration serial number.
        
        Args:
            serial (str): The serial number.
        
        Returns:
            tuple: (bool, str) Success status and message.
        """
        section, key = self.topic_serial.split(".")
        try:
            self.toml_data[section][key] = serial
            return True, f"Serial number set to: {serial}"
        except Exception as e:
            return False, f"Error setting serial number in configuration: {e}"
    
    def set_configuration_client_id(self, client_id):
        """
        Set the configuration MQTT client_id.
        
        Args:
            client_id (str): The client_id.
        
        Returns:
            tuple: (bool, str) Success status and message.
        """
        section, key = self.topic_client_id.split(".")
        try:
            self.toml_data[section][key] = client_id
            return True, f"Client ID set to: {client_id}"
        except Exception as e:
            return False, f"Error setting Client ID in configuration: {e}"

    def set_configuration_mqtt_broker_ip(self, broker):
        """
        Set the MQTT broker's IP .
        
        Args:
            broker (str): The MQTT broker's IP
        
        Returns:
            tuple: (bool, str) Success status and message.
        """
        section, key = self.topic_broker_ip.split(".")
        try:
            self.toml_data[section][key] = broker
            return True, f"MQTT broker IP set to: {broker}"
        except Exception as e:
            return False, f"Error setting MQTT broker's IP in configuration: {e}"
    
    def update_toml_data(self, section, key, value):
        """
        Update TOML data with new values.
        
        Args:
            section (str): The section of the TOML file.
            key (str): The key to update.
            value: The new value to set.
        """
        if section:
            self.toml_data[section][key] = self.parse_value(value, self.toml_data[section][key])
        else:
            self.toml_data[key] = self.parse_value(value, self.toml_data[key])
    
    def parse_value(self, value, original):
        """
        Convert user input to the appropriate data type.
        
        Args:
            value: The input value.
            original: The reference data type.
        
        Returns:
            Converted value in the correct type.
        """
        if isinstance(original, bool):
            return value.lower() in ("true", "1", "yes")
        elif isinstance(original, int):
            return int(value)
        elif isinstance(original, float):
            return float(value)
        return value
    
    def scan_firmware(self):
        """
        Scan the firmware directory for available versions.
        """
        pass
    
    @property
    def templates(self):
        """
        Retrieve a list of available TOML templates.
        
        Returns:
            list: List of template filenames.
        """
        return [i for i in os.listdir(os.path.abspath(self.template_dir)) if i.endswith('.toml')]
    
    def set_template(self, selection):
        """
        Set the template to be used.
        
        Args:
            selection (str): The name of the template to use.
        """
        self.template = selection 
        
    def write_configuration(self):
        """
        Write the current configuration to the device.
        """
        self.read_settings_to_temp()
        for group in self.toml_data.keys():
            for parameter in self.toml_data[group].keys():
                if f"{group}.{parameter}" not in self.parameters_ignore:
                    if group in self.temp_toml_data and parameter in self.temp_toml_data[group]:
                        if self.toml_data[group][parameter] != self.temp_toml_data[group][parameter]:
                            superuser = f"{group}.{parameter}" in self.parameters_superuser
                            print(f"Setting parameter '{group}.{parameter}' to '{self.toml_data[group][parameter]}'")
                            print(f'Result: {self.set(group, parameter, self.toml_data[group][parameter], superuser)}')
                            print(f"Parameter '{group}.{parameter}' is now set to {self.get(group, parameter)}")
                    else:
                        print(f"Parameter '{group}.{parameter}' is not available in this firmware!")
        #time.sleep(1)
        return True
    
    def get(self,group, parameter):
        return self.PS280.get(group, parameter)
        
    def set(self, group, parameter, value= None, superuser=False):
        result= False
        # try:
        result=self.PS280.set(group, parameter, value, superuser)
        #  except Exception as e:
        #     print(f'Could not set parameter {group}.{parameter}:\n {e}', file=sys.stderr)
        return result
        
    @property
    def firmware_versions(self):
        """
        Retrieve a list of available firmware versions.
        
        Returns:
            list: List of firmware version directories.
        """
        return [i for i in os.listdir(os.path.abspath(self.firmware_dir)) if os.path.isdir(os.path.abspath(os.path.join(self.firmware_dir, i)))]
    
    def set_firmware_version(self, selection):
        """
        Set the desired firmware version and assign associated files.
        
        Args:
            selection (str): Firmware version directory.
        """
        self.firmware['version'] = selection
        bin_files = [i for i in os.listdir(os.path.abspath(os.path.join(self.firmware_dir, selection))) if i.endswith('.bin')]
        for bf in bin_files:
            if bf.startswith('boot'):
                self.firmware['bootloader'] = bf
            elif bf.startswith('partition'):
                self.firmware['partitiontable'] = bf
            elif bf.startswith('pikk-sense-'):
                self.firmware['firmwarebin'] = bf
    
    def connect(self):
        """
        Establish a connection to the PS-280 device.
        """
        #del self.PS280
        #time.sleep(5)
        print("Connecting to PS-280")
        self.PS280 = PS280('', 115200, timeout=1, stdout=stdoutstream, stderr=stderrstream)
        print("------",self.PS280.connection)
        if self.PS280.connection is None:
            print('No connection to PS-280', file=sys.stderr)
            del self.PS280
            raise Exception("No PS-280 availabe")
            return False
        return True
        
    def firmware_erase(self):
        """
        Erase the firmware from the PS-280 device.
        
        Returns:
            bool: True if firmware was erased successfully, False otherwise.
        """
        print("Erasing firmware on PS-280")
        result = False
        
        if self.PS280 is None:
            print('No connection to PS-280', file=sys.stderr)
            return False
#        try:
#            self.PS280.serial_reconnect()  # Check if device is connected
#        except Exception as e:
#            print(f'No connection to PS-280: {e}', file=sys.stderr)
#            return False
        try:
            result = self.PS280.firmware_erase()
            time.sleep(1)
        except Exception as e:
            print(f'Error erasing firmware: {e}', file=sys.stderr)
        return not result

    def firmware_flash(self):
        """
        Flash firmware onto the PS-280 device.
        
        Returns:
            bool: True if flashing was successful, False otherwise.
        """
        print("Flashing firmware on PS-280")
        result = False
        if self.PS280 is None:
            print('No connection to PS-280', file=sys.stderr)
            return False
#        try:
#            self.PS280.serial_reconnect()  # Check if device is connected
#        except Exception as e:
#            print(f'No connection to PS-280: {e}', file=sys.stderr)
#            return False
        try:
            # Update firmware with the corresponding files
            result = self.PS280.firmware_update(
                bootloader_file=f"{os.path.join(os.path.abspath(self.firmware_dir), self.firmware['version'], self.firmware['bootloader'])}",
                partition_table_file=f"{os.path.join(os.path.abspath(self.firmware_dir), self.firmware['version'], self.firmware['partitiontable'])}",
                firmware_file=f"{os.path.join(os.path.abspath(self.firmware_dir), self.firmware['version'], self.firmware['firmwarebin'])}"
            )
            time.sleep(1)
        except Exception as e:
            print(f'Error flashing firmware: {e}', file=sys.stderr)
        return not result

    def read_settings(self):
        print("Reading settings from PS-280\nPlese be patient...")
        if self.PS280 is None:
            print('No connection to PS-280', file=sys.stderr)
        else:
            print( 'Reading')
            config_data= self.PS280.settings
            #time.sleep(1)
            if config_data:
                self.toml_data= config_data
                return True
            return False

    def read_settings_to_temp(self):
        print("Reading settings from PS-280\nPlese be patient...")
        if self.PS280 is None:
            print('No connection to PS-280', file=sys.stderr)
        else:
            print( 'Reading')
            config_data= self.PS280.settings
            #time.sleep(1)
            if config_data:
                self.temp_toml_data= config_data
                return True
            return False
    
    
    @property
    def sensor_id(self):
        """
        Retrieve the sensor ID from the TOML configuration.
        
        Returns:
            str: Sensor ID in formatted string.
        """
        section, key = self.topic_upload.split(".")
        rawtopic = self.toml_data[section][key].split('/')
        position_id = '.'.join(rawtopic[1:-1])
        sensor = rawtopic[-1]
        return f'{position_id}:{sensor}'
    
    @property
    def serial_number(self):
        """
        Retrieve the serial number from the TOML configuration.
        
        Returns:
            str: Serial number string.
        """
        section, key = self.topic_serial.split(".")
        try:
            return self.toml_data[section][key]
        except KeyError:
            return ''

    @property
    def firmware_version(self):
        """
        Retrieve the firmware version from the TOML configuration.
        
        Returns:
            str: Firmware version as a string.
        """
        section, key = self.topic_version.split(".")
        try:
            return self.toml_data[section][key]
        except KeyError:
            return ''
    
    @property
    def mqtt_broker_ip(self):
        """
        Retrieve the MQTT broker IP from the TOML configuration.
        
        Returns:
            str: MQTT broker IP address.
        """
        section, key = self.topic_broker_ip.split(".")
        try:
            return self.toml_data[section][key]
        except KeyError:
            return ''
    
    def create_stickers(self):
        """
        Generate a sticker with a QR code based on device configuration data.
        
        The sticker contains relevant device information including serial number and sensor ID,
        and is saved as a high-resolution image.
        """

        def open_file(filepath):
            
            # Open with default viewer (Windows, macOS, Linux compatible)
            if sys.platform == "darwin":
                subprocess.run(["open", filepath])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", filepath])
            else:
                subprocess.run(["start", filepath], shell=True)
            
        targetpath = os.path.dirname(os.path.join(self.current_file_path))
        
        # Initialize sticker generator with configuration files
        sticker = Sticker(configfile=self.sticker_config_file, 
                          image_template=self.sticker_template_file, 
                          output_path=targetpath)
        
        sticker.read_configuration()
        sticker.serial = self.serial_number
        sticker.sensorid = self.sensor_id
        
        # Create sticker and QR code
        sticker.create_sticker(size=50, show=False)
        sticker.create_qr_code(size=35, show=False)
        
        # Load generated images
        qr_image = Image.open(sticker.qr_code_file).convert('RGBA')
        sticker_image = Image.open(sticker.image_file).convert('RGBA')
        
        # Compute the size of the combined image
        merged_width = max(qr_image.width, sticker_image.width)
        merged_height = qr_image.height + sticker_image.height
        
        # Create a blank image with transparent background
        merged_image = Image.new('RGBA', (merged_width, merged_height))
        
        # Paste QR code and sticker onto the merged image
        merged_image.paste(qr_image, (0, 0))
        merged_image.paste(sticker_image, (0, qr_image.height))
        
        # Save the final high-resolution image
        filepath = os.path.join(sticker.output_path, f"{sticker.serial}_qr_and_sticker.png")
        merged_image.save(filepath, dpi=(300, 300))
        open_file(sticker.qr_code_file)
        open_file(sticker.image_file)


