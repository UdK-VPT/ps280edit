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

# + editable=true slideshow={"slide_type": ""} language="html"
# <style>
# table {float:left}
# </style>
# -

# ## Parameter Description for PIKK Systems PS-280 Sensors
#
# ### Parametergroup *CORE* -> Basic settings and parameters
#     
# |Group|Parameter|ReadOnly|Default Value|Description|
# |:------------------|:------------------|:--------------------------------------------------------------:|:------------------:|:------------------|
# |CORE|BCMP||1|
# |CORE|CPORT           |    X  |  0|
# |CORE|MSC        ||              4|
# |CORE|MSI         ||             300|
# |CORE|SERIAL          |    X  |  PS280-123456|
# |CORE|TRANSPORT                modem|
#     

# ### Parametergroup *HUB*
#
# ['HUB', 'TSYNC_WAIT', '1']
# ['HUB', 'LIFETIME', '300']
# ['HUB', 'PROTOCOL', 'tcp']
# ['HUB', 'REMOTE_IP', 'mm.mosquitto.org']
# ['HUB', 'REMOTE_PORT', '1883']
# ['HUB', 'TYPE', 'mqtt']
# ### Parametergroup *CORE*
#
# ['MODEM', 'BANDS', '8,', '20,']
# ['MODEM', 'APN', 'gigsky-02']
# ['MODEM', 'OP', '0']
#
# ### Parametergroup *CORE*
#
# ['MQTT', 'TIMEOUT', '15']
# ['MQTT', 'MAX_RETRY', '4']
# ['MQTT', 'QOS', '1']
# ['MQTT', 'TOPIC_DOWN', 'PS-280/down']
# ['MQTT', 'TOPIC_UP', 'PS-280/up']
#
# ### Parametergroup *CORE*
#
# ['SEC', 'LOG_LEVEL', '0']
# ['SEC', 'CA_PATH', '/sec/ca.pem']
# ['SEC', 'CC_PATH', '/sec/cc.pem']
# ['SEC', 'MODE', '0']
#
# ### Parametergroup *SENSOR*
#
# ['SENSOR', 'DTO', '100']
#
# ### Parametergroup *COSIGRE*
#
# ['SIG', 'REG_VIS', '1']
# ['SIG', 'BOOT_AUR', '1']
# ['SIG', 'BOOT_VIS', '1']
#
# ### Parametergroup *CORE*
#
# THRESH    SUNRISE_CO2_ENA          0
#
# THRESH    SUNRISE_CO2_LO           0
#
# THRESH    SUNRISE_CO2_HI           1000
#
# THRESH    AHT_HUM_ENA              0
#
# THRESH    AHT_HUM_HI               1000
#
# THRESH    AHT_HUM_LO               -1000
#
# THRESH    AHT_TEM_ENA              0
#
# THRESH    AHT_TEM_HI               1000
#
# THRESH    AHT_TEM_LO               -1000
#
# ### Parametergroup *WIFI*
#
# WIFI      AP_SEC                   wpa2_psk
#
# WIFI      AP_PW                    
#
# WIFI      AP_SSID                  default_ap

# +
import sys, serial, time, json, logging, warnings, toml, copy
from contextlib import redirect_stdout
#from benedict import benedict
import esptool, time, os, io
import subprocess
import select
import glob
import re

# Clear any default root logger handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Create a custom logger
logger = logging.getLogger("stderr_logger")
logger.setLevel(logging.DEBUG)  # Capture all levels

# Prevent duplication by disabling propagation
logger.propagate = False

# Create handlers
stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)

# Set levels for handlers
stdout_handler.setLevel(logging.INFO)   # INFO and below
stderr_handler.setLevel(logging.ERROR)  # ERROR and above

# Create formatters and add them to handlers
stderrformatter = logging.Formatter('%(levelname)s: - %(message)s')
stdoutformatter = logging.Formatter('%(levelname)s: - %(message)s')
stdout_handler.setFormatter(stdoutformatter)
stderr_handler.setFormatter(stderrformatter)

# Add handlers to the logger
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)

def printerror(message):
    print(message, file=sys.stderr)

def startprogress(title):
    print(f"{title} ")
    
def printprogress():
    print('.',end='')

def endprogress():
    print("\n")
#logger.basicConfig(format='%(asctime)s-%(levelname)s: %(message)s', 
#                    level=logger.INFO)

def clean_vt100(data):
    """
    Removes VT-100 ANSI escape codes and non-printable characters.
    """
    # Comprehensive ANSI escape code pattern for VT-100
    ansi_escape = re.compile(r'(\x1b[@-_][0-9;?]*[ -/]*[@-~])')
    
    # Remove ANSI escape sequences
    data = ansi_escape.sub('', data)

    # Remove non-printable characters and control sequences
    printable = re.compile(r'[^\x20-\x7E\n\r\t]')
    data = printable.sub('', data)

    # Collapse repetitive patterns and remove stray ANSI color codes
    repetitive = re.compile(r'(/[ >�]+)+')
    data = repetitive.sub('/ > ', data)

    # Remove residual garbage characters
    residual = re.compile(r'�+')
    data = residual.sub('', data)

    return data.strip()

    
class PS280:

    def __init__(self,port='', baudrate=115200, timeout=3, stdout= sys.stdout, stderr= sys.stderr):
        self.stdout= stdout
        self.stderr= stderr
        if port:
            self.port= port
        else:
            self.port= None
        self.baudrate= baudrate
        self.timeout= timeout
        self.connection= None
        #self.check_serialport
        self.serial_reconnect()
    
    def open_serial(self):
        """
        Try to open the given serial port.
        """
        # clear serial
        try:
            del self.connection
            self.connection= None
        except:
            pass
        if self.port:
            try:
                ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                logger.info(f"Connected to {self.port}")
                self.connection= ser
                return True
            except serial.SerialException as e:
                logger.error(f"Error opening {self.port}: {e}")
                printerror(f"Error opening {self.port}: {e}")
        
                self.connection= None
        logger.error(f"Could not connect to device")        
        printerror(f"Could not connect to device")        
        return False
    
    def check_chiptype(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            esptool.main(['read_mac'])
            output = buf.getvalue()
        output= output.split('\n')
        for n, sp in enumerate(output):
            print(n, sp )
            if sp.startswith('Detecting chip type'):
                return(output[n].split(' ')[-1])
        return('Unknown')

    
    def serial_reconnect(self):
        """
        Continuously check for USB serial connection and handle reconnections.
        """
        
        #while True:
        if self.connection and self.connection.is_open:
            return True
        print("Searching for ESP device...")
        if self.find_esp_port():
            self.open_serial()
        #time.sleep(0.5)
        return self.connection
        
    def find_esp_port(self, retries=10):
        """
        Combines pySerial scanning and esptool detection to find ESP device.
        """
        esp_vids = {
            "1A86:7523": "CH340",
            "10C4:EA60": "CP210x",
            "0403:6001": "FT232",
            "067B:2303": "PL2303",
            "303A:1001": "Espressif USB JTAG/serial debug unit",
            "10C4:EA60": "Silabs CP2102N"
        }
        logger.info("find_esp_port()")
        startprogress("Trying to connect")
        while retries:
            ports = serial.tools.list_ports.comports()
            candidate_ports = []
            #print(ports)
            # Step 1: Quick scan using pySerial
            for port in ports:
                #print(port.hwid, port.pid)
                if any(vid in port.hwid for vid in esp_vids) :
                    logger.info(f"Possible ESP device on port: {port.device}")
                    candidate_ports.append(port.device)
        
            # Step 2: Validate with esptool
            for port in candidate_ports:
                try:
                    logger.info(f"Verifying with esptool on port: {port}")
                    esptool.main(["--port", port, "flash_id"])
                    logger.info(f"ESP device confirmed on port: {port}")
                    self.port=port
                    return True
                except Exception:
                    logger.info(f"Port {port} did not respond as ESP.")
            time.sleep(1)
            retries -= 1
            printprogress()
        endprogress()
        self.port= None
        printerror("No ESP device found.")
        logger.error("No ESP device found.")
        time.sleep(2)
        return False

        
    def check_serialport(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            esptool.main(['read_mac'])
            output = buf.getvalue()
        output= output.split('\n')
        for n, sp in enumerate(output):
            if sp.startswith('Detecting chip type'):
                return(output[n-2].split(' ')[-1])
        return('')

    @property
    def connected(self):
        try:
            self.connection.write(b'teststring\r\n')
            return True
        except:
            self.connection= None
            return False

    def check_connection(self):
        if not self.connected():
                raise Exception('Device is not answering!')

    def send_command(self, command, starttoken='', endtoken='', errortoken= '',timeout=2):
        """
        Sends a command and reads the complete response.
        Args:
        command (str): The command to send.
            starttoken (str): Optional token indicating the start of the response.
            endtoken (str): Optional token indicating the end of the response.
            timeout (int): Maximum time to wait for the complete response (seconds).
        Returns:
            list: The complete response as a list of cleaned strings.
        """
        # Step 1: Clear any residual data before sending the command
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        # Short delay to ensure buffer clearing
        time.sleep(0.1)  
    
        # Step 2: Send the command with CR line ending
        self.connection.write((command + '\r\n\r\n').encode('utf-8'))
        print(f"Sent: {command}")
        # Allow some time for the device to process
        time.sleep(0.1)  
    
        start_time = time.time()
        response = []
        start_found = False
    
        # Step 3: Read the response until end token or timeout
        while time.time() - start_time < timeout:
            # Check if data is available
            if self.connection.in_waiting:
                # Read and clean the data
                raw_data = self.connection.readline().decode('utf-8', errors='ignore')
                data = clean_vt100(raw_data).strip()
                #print(data)
                if errortoken and errortoken in data:
                    logger.error('Illegal value!')
                    return [errortoken]
                # Detect the start token if specified
                if starttoken and starttoken in data:
                    start_found = True
                    # Skip the start token if no end token is specified
                    if not endtoken:
                        return [starttoken]
    
                # Append data to response if start token was found
                if start_found:
                    if endtoken in data:
                        # Stop if the end token is detected
                        break  
                    # Only append non-empty cleaned data
                    if data:  
                        response.append(data)
            else:
                # Avoid CPU overload
                time.sleep(0.01)  
    
        # Return the collected response
        return response
    
    def read_settings_file(self):
        logger.info('Reading all settings')
        settings= ''
        #self.connection.reset_input_buffer()
        #self.connection.reset_output_buffer()
        #self.connection.readlines(-1)
        self.connection.write(b'cat /core/settings\r\n')
        time.sleep(0.5)          
        for line in self.connection.readlines(-1):
            if '{"CORE":[' in line.decode('utf-8'):
                settings = eval('{"CORE":['+line.decode('utf-8').split('{"CORE":[')[-1])
        settings= eval({k:{p['name']:p['value'] for p in g} for k,g in settings.items()})
        return (settings)

    def get(self,group,parameter):
        return(self.settings[group][parameter ])

    def set(self,group,parameter,value, superuser=False):
        group= group.upper()
        parameter= parameter.upper()
        value= str(value)
        logger.info(f"Setting parameter '{group}.{parameter}' to value '{value}'!")
        if superuser:
            self.connection.write('su PS!_@dmin\r\n'.encode('utf_8'))
            time.sleep(0.3)

        while not (response := self.send_command(f"settings set {group} {parameter} {value}", starttoken='stored', endtoken='', errortoken= "illegal value")):
            time.sleep(0.5)
        print(f'[{group}][{parameter}] is set to {self.settings[group][parameter]}')
        return(response)

    def info(self,group,parameter):
        logger.info(f"Getting parameter info for '{group}.{parameter}'!")
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        self.connection.write(f'settings info {group} {parameter}\r\n'.encode('utf_8'))
        #logger.info('Waiting for Results...')
        time.sleep(0.1)
        #time.sleep(0.5)
        
        result= self.receive() #self.connection.readlines(-1)
        return(result)   

    @property
    def settings(self):
        
        while not (response := self.send_command("settings", starttoken='Module', endtoken='/ >')):
            time.sleep(0.5)
        settings= {}
        for line in response[1:]:
            line= ' '.join(line.strip().split()).split(' ')
            if line and line[0].isalnum():
                if line[0] not in settings:
                    settings[line[0]]={}
                if len(line) > 2:
                    settings[line[0]][line[1]] = line[-1]
                elif len(line) > 1:
                    settings[line[0]][line[1]] =  ""
        return(settings)
        

    def info_dict(ps, group , parameter):
        info=ps.info(group,parameter)
        infodict={'group': group,
                  'parameter': parameter,
                  'shortDescription': '',
                  'minimumValue': '',
                  'maximumValue': '',
                  'allowedValues': ''}
        if not [i for i in info if i.endswith('unknown setting\n')]:
            for i in info:
                #print(i)
                if i.startswith('Info:'):
                    if len(i := i.split(': ')) > 1:
                        infodict['shortDescription']=i[1].strip()
                elif i.startswith('Min. value:'):
                    if len(i := i.split(': ')) > 1:
                        infodict['minimumValue']=i[1].strip()
                elif i.startswith('Max. value:'):
                    if len(i := i.split(': ')) > 1:
                        infodict['maximumValue']=i[1].strip()
                elif i.startswith('Allowed:'):
                    if len(i := i.split(': ')) > 1:
                        infodict['allowedValues']=i[1].strip().strip('{}').split(',')
        return(infodict)


    def clear_buffers(self):
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        
    def reboot(self):
        logger.info('Rebooting')
        self.clear_buffers()
        self.connection.write('reboot\r\n'.encode('utf_8'))

    @staticmethod
    def run_command_with_realtime_output(command):
        # Set up environment to disable Python buffering (for Python subprocesses)
        env = os.environ.copy()
        if "python" in command[0].lower() or command[0] == sys.executable:
            env["PYTHONUNBUFFERED"] = "1"
        
        # Start the subprocess with pipes for stdout and stderr
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1  # Line-buffered
        )
        
        # Non-blocking read loop using select (works on Unix and Windows)
        while True:

            readable, _, _ = select.select([process.stdout, process.stderr], [], [])
            stdout_line=''
            # Check stdout
            if process.stdout in readable:
                stdout_line = process.stdout.readline()
                if stdout_line:
                    sys.stdout.write(stdout_line)
        
            # Check stderr
            if process.stderr in readable:
                stderr_line = process.stderr.readline()
                if stderr_line:
                    sys.stderr.write(stderr_line)
        
            # Exit the loop when the process is done and both streams are empty
            if process.poll() is not None and not stdout_line and not stderr_line:
                break
        if process.returncode != 0:
            raise Exception(f"esptool ould not finish commend execution {command}")
        return process.returncode

    @staticmethod
    def firmware_erase():
        logger.info('Erasing flash... (This may take a while!)')
        return not PS280.run_command_with_realtime_output([sys.executable, "-m", "esptool", "-b", "460800", "erase_flash"])
        
    
    @staticmethod
    def firmware_update(bootloader_file, partition_table_file,firmware_file):
        logger.info('Updating firmware')
        return not PS280.run_command_with_realtime_output( 
            [
                sys.executable, "-m", "esptool", "-b", "460800", "write_flash",
                "0x0000", bootloader_file,
                "0x8000", partition_table_file,
                "0x10000", firmware_file
                ]
            )

# -

