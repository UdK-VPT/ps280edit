# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
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
import sys, serial, time, json, warnings, logging, toml, copy
from contextlib import redirect_stdout
#from benedict import benedict
import esptool, time, os, io
import subprocess
import select



logging.basicConfig(format='%(asctime)s-%(levelname)s: %(message)s', level=logging.INFO)

class PS280_Warning(UserWarning):
    print()
    pass

class Configuration:
    
    @staticmethod
    def _flatten(dictionary):
        out={}
        for group in dictionary:
            out.update({f'{group}.{parameter}': dictionary[group][parameter] for parameter in dictionary[group]})
        return(out)
        
    def __init__(self, configfile = '', configdict = {}, read=False):
        self.configfile = configfile
        self._configuration = configdict
        if read:
            self.read()

    def read(self, configfile = ''):
        if not configfile:
            configfile = self.configfile
        logging.info(f"Reading configuration to '{configfile}'")
        with open(configfile, 'r') as f:
            self._configuration = toml.load(f)
        return(self._configuration)
    
    def write(self, configfile = ''):
        if not configfile:
            configfile = self.configfile
        logging.info(f"Writing configuration to '{configfile}'")  
        with open(configfile,'w') as f:
            toml.dump(self._configuration, f)
        
    def get(self, group = '', parameter = '', field = '', flattened= False):
        out = {}
        if group:
            if parameter:
                if field:
                    out = self._configuration[group][parameter][field]
                else:            
                    out = self._configuration[group][parameter]
            else:
                for p in self._configuration[group]:
                    out = {p: self.get(group,p,field) for p in self._configuration[group]}
        else:
            for g in self._configuration:
                out[g]={}
                for p in self._configuration[g]:
                        out[g][p] = self.get(g,p,field)
        if flattened:
            return(self._flatten(out))
        return(out)
    
    def set(self, group = '', parameter = '', field = '', value= None):
        self._configuration[group][parameter][field] = value
        
    @property
    def fields(self):
        return(list(self._configuration[next(iter(self._configuration))].keys()))

    @property
    def groups(self):
         return(list(self._configuration))
        
    @property
    def parameters(self):
        return({g:list(self._configuration[g].keys()) for g in self._configuration})

    def capture_from_sensor(self, configfile = '', save= False):
        logging.info(f"Capturing configuration from sensor")
        sensor= PS280()
        settings= sensor.settings()
        logging.info('Capturing all setting and infos')
        for group,pset in settings.items():
            self._configuration[group] = {}
            for parameter,value in pset.items():
                #initialize parameter set, 
                #set factoryValue to value found on ps-2820 (only use after firmware update)
                #set controlType to text_input as default
                self._configuration[group][parameter]={"shortDescription":'',
                                            "longDescription":'',
                                            "controlType":'text_input',
                                            "minimumValue":'',
                                            "maximumValue":'',
                                            "allowedValues":'',
                                            "factoryValue": value,
                                            "defaultValue": '',
                                            "provisionalValue": '',
                                            "value": ''}
                #get info from ps-280
                info = sensor.info_dict(group , parameter)
                #set items of parameter set to received values
                for k,v in info.items():
                    self._configuration[group][parameter][k] = v 
                    
                #find control type
                if self._configuration[group][parameter]["allowedValues"]:
                    if self._configuration[group][parameter]["factoryValue"].startswith('[') and self._configuration[group][parameter]["factoryValue"].endswith(']'):
                        self._configuration[group][parameter]["controlType"] = 'multiselect_box'
                    else:
                        self._configuration[group][parameter]["controlType"] = 'select_box'
                elif (self._configuration[group][parameter]["minimumValue"] == '0') and (self._configuration[group][parameter]["maximumValue"] == '1'):
                    self._configuration[group][parameter]["controlType"] = 'checkbox'
                else:
                    try:
                        mi = int(self._configuration[group][parameter]["minimumValue"])
                        ma = int(self._configuration[group][parameter]["maximumValue"])
                        if (ma - mi) < 50:
                            self._configuration[group][parameter]["controlType"] = 'slider'
                    except:
                        pass
                #force text_input on specific parameters
                if f'{group}.{parameter}' in ['CORE.SERIAL','HUB.TYPE']:
                    self._configuration[group][parameter]["controlType"] = 'text_input'
                #convert values based on the controlType (necessary for multiselect_box, checkbox, slider  )
                
                #logging.info(self._configuration[group][parameter]["value"])
                if self._configuration[group][parameter]["controlType"] == 'multiselect_box':
                    self._configuration[group][parameter]["factoryValue"] = self._configuration[group][parameter]["factoryValue"].strip('[').strip(']').split(',')
                elif self._configuration[group][parameter]["controlType"] == 'checkbox':
                    self._configuration[group][parameter]["factoryValue"] = bool(int(self._configuration[group][parameter]["factoryValue"]))
                    self._configuration[group][parameter]["minimumValue"] = bool(int(self._configuration[group][parameter]["minimumValue"]))
                    self._configuration[group][parameter]["maximumValue"] = bool(int(self._configuration[group][parameter]["maximumValue"]))
                elif self._configuration[group][parameter]["controlType"] == 'slider':
                    self._configuration[group][parameter]["factoryValue"] = int(self._configuration[group][parameter]["factoryValue"])
                    self._configuration[group][parameter]["minimumValue"] = int(self._configuration[group][parameter]["minimumValue"])
                    self._configuration[group][parameter]["maximumValue"] = int(self._configuration[group][parameter]["maximumValue"])

                #copy.deepcopy() is necessary to avoid references and anchors in the toml file
                self._configuration[group][parameter]["defaultValue"] = copy.deepcopy(self._configuration[group][parameter]["factoryValue"])
                self._configuration[group][parameter]["value"] = copy.deepcopy(self._configuration[group][parameter]["factoryValue"])
                self._configuration[group][parameter]["provisionalValue"] = copy.deepcopy(self._configuration[group][parameter]["factoryValue"])
                #logging.info(self._configuration[group][parameter]["controlType"])
                #logging.info(self._configuration[group][parameter]["value"])
        if save:
            self.write()
        return(self._configuration)
    
    
class PS280:
    
    class switch:
        def __init__(self, outer_instance ,group, parameter):
            self.outer= outer_instance
            self.group= group
            self.parameter= parameter

        def on(self):
            self.outer.set(self.group, self.parameter, '1')

        def off(self):
            self.outer.set(self.group, self.parameter, '0')

        def enable(self):
            self.on()

        def disable(self):
            self.off()

    class warning:
        def __init__(self, outer_instance ,group, parameter_low, parameter_high, parameter_enable= '', lowest=- 1000, highest= 1000):
            self.outer= outer_instance
            self.group= group
            self.parameter_low= parameter_low
            self.parameter_high= parameter_high
            self.parameter_enable= parameter_enable
            self.lowest= lowest
            self.highest= highest
            self._high=''
            self._low=''


        def set_low(self, low):
            if low:
                self._low= str(low)
            if self._low:

                self.outer.set(self.group, self.parameter_low, self._low)

        def reset_low(self):
            self.outer.set(self.group, self.parameter_low, self.lowest)

        def set_high(self, high):
            if high:
                self._high= str(high)
            if self._high:
                self.outer.set(self.group, self.parameter_high, self._high)

        def reset_high(self):
            self.outer.set(self.group, self.parameter_high, self.highest)

        def on(self, low='', high=''):
            if self.parameter_enable:
                self.outer.set(self.group, self.parameter_enable, 1)
            self.set_low(low)
            self.set_high(high)

        def off(self):
            self.reset_low()
            self.reset_high
            if self.parameter_enable:
                self.outer.set(self.group, self.parameter_enable, 0)

        def enable(self, low='', high=''):
            self.on(low, high)

        def disable(self):
            self.off()
            

            
    def find_serial_port(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            esptool.main(['read_mac'])
            output = buf.getvalue()
        output= output.split('\n')
        for n, sp in enumerate(output):
            if sp.startswith('Detecting chip type'):
                return(output[n-2].split(' ')[-1])
        return('')
        
        
       # with io.StringIO() as buf, redirect_stdout(buf):
      #      esptool.main(['read_mac'])
       #     output = buf.getvalue()
       # output= output.split('\n')
      # if [sp for sp in output if sp.startswith('Detecting chip type')][-1]:
      #      return([sp for sp in output if sp.startswith('Serial port')][0].split(' ')[2])
       # return('')

    def __init__(self,port='', baudrate=115200, timeout=3, stdout= sys.stdout, stderr= sys.stderr):
        self.stdout= stdout
        self.stderr= stderr
        if port:
            self.port= port
        else:
            self.port= self.find_serial_port()
        self.connection= serial.Serial(self.port, baudrate, timeout=timeout)
        self.aural_boot_signal= self.switch(self, 'SIG', 'BOOT_AUR')
        self.visual_registration_signal= self.switch(self, 'SIG', 'REG_VIS')
        self.visual_boot_signal= self.switch(self, 'SIG', 'BOOT_VIS')
        
        self.co2_warning= self.warning(self, 'THRESH', 'SUNRISE_CO2_LO', 'SUNRISE_CO2_HI', '', 0, 1000)
        self.humidity_warning= self.warning(self, 'THRESH', 'AHT_HUM_LO', 'AHT_HUM_HI','AHT_HUM_ENA', -100, 200)
        self.temperature_warning= self.warning(self, 'THRESH', 'AHT_TEM_LO', 'AHT_TEM_HI','AHT_TEM_ENA', -100, 100)

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

    
    def receive(self, timeout=10):
        #this will store the line
        seq = []
        lines = []
        count = 1
        #while self.connection.in_waiting < 80:
        #    time.sleep(0.1)
        while True:
            line = self.connection.readline().decode('utf-8')
            #print("LINE", line, "END")
            if (line := line.strip()):# and (not line.strip().endswith('/ >'))):
                if not line.strip().endswith('/ >'):
                    lines.append(line)
            else:
                break
        return(lines)
    
    def read_settings_file(self):
        logging.info('Reading all settings')
        settings= ''
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        self.connection.write(b'cat /core/settings\r\n')
        time.sleep(0.5)          
        for line in self.connection.readlines(-1):
            if '{"CORE":[' in line.decode('utf-8'):
                settings = eval('{"CORE":['+line.decode('utf-8').split('{"CORE":[')[-1])
        settings= eval({k:{p['name']:p['value'] for p in g} for k,g in settings.items()})
        return (settings)

    def get(self,group,parameter):
        return(self.settings()[group][parameter ])

    def set(self,group,parameter,value, superuser=False):
        logging.info(f"Setting parameter '{group}.{parameter}' to value '{value}'!")
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        if superuser:
            self.connection.write('su PS!_@dmin\r\n'.encode('utf_8'))
        time.sleep(0.3)
       # self.connection.readlines(-1) ###############TTTEEESSSTT
       # time.sleep(0.1)
        self.connection.write(f'settings set {group} {parameter} {value}\r\n'.encode('utf_8'))
        time.sleep(0.3)
        result= self.connection.readlines(-1)
        textresult=[r.decode('utf-8') for r in result if not r.decode('utf-8').endswith('> \n')]
        logging.info(f"Setting parameter '{group}.{parameter}' to value '{value}'!")
        logging.info(f'###{textresult}###')
        #logging.info(' '.join(textresult), PS280_Warning)
        if b'stored' not in b' '.join(result):
            logging.info(' '.join(textresult), PS280_Warning)
            return(False)
        else:
            logging.info('Done!')
        return(True)

    def info(self,group,parameter):
        logging.info(f"Getting parameter info for '{group}.{parameter}'!")
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        self.connection.write(f'settings info {group} {parameter}\r\n'.encode('utf_8'))
        #logging.info('Waiting for Results...')
        time.sleep(0.1)
        #time.sleep(0.5)
        
        result= self.receive() #self.connection.readlines(-1)
        return(result)   

    
    def settings(self, printout=False):
        settings= {}
       # print(0)
        #self.check_connection()
       # print('.', end='')
        logging.info(f"Getting settings...")
        self.connection.reset_input_buffer()
       # print('.', end='')
        self.connection.reset_output_buffer()
        self.connection.write(f'settings get\r\n'.encode('utf_8'))
        time.sleep(0.5)
        #find start
       # print('.', end='')
        timeout_cnt=100
       # print('.', end='')
        received= self.connection.readline().decode('utf-8')
        while 'Module' not in received:
            if timeout_cnt == 0:
                raise Exception('The device did not answer')
            timeout_cnt -= 1
            time.sleep(0.1)
            received= self.connection.readline().decode('utf-8')
       # print('.', end='')
        while "\n" == self.connection.readline().decode('utf-8'):
            logging.info('Waiting for \\r')
        
        while  line:=self.connection.readline().decode('utf-8'):#) != "\n" :#.strip():
            #logging.info(line)
            line= ' '.join(line.strip().split()).split(' ')
            if line and line[0].isalnum():
                if line[0] not in settings:
                    settings[line[0]]={}
                if len(line) > 2:
                    settings[line[0]][line[1]] = line[-1]
                elif len(line) > 1:
                    settings[line[0]][line[1]] =  ""
       # print('.', end='\r')
        if printout:
            print(toml.dump(settings, allow_unicode=True, default_flow_style=False))
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

    def capture_factory_defaults(self, filepath= 'firmware_defaults.toml'):
        settings= self.settings()
        logging.info('Capturing all setting and infos')
        for group,pset in settings.items():
            for parameter,value in pset.items():
                #initialize parameter set, 
                #set factoryValue to value found on ps-2820 (only use after firmware update)
                #set controlType to text_input as default
                settings[group][parameter]={"shortDescription":'',
                                            "longDescription":'',
                                            "controlType":'text_input',
                                            "quickAccess": False,
                                            "minimumValue":'',
                                            "maximumValue":'',
                                            "allowedValues":'',
                                            "factoryValue": value,
                                            "defaultValue": '',
                                            "provisionalValue": '',
                                            "value": ''}
                #get info from ps-280
                info = self.info_dict(group , parameter)
                #set items of parameter set to received values
                for k, v in info.items():
                    settings[group][parameter][k] = v 
                #find control type
                if settings[group][parameter]["allowedValues"]:
                    if settings[group][parameter]["factoryValue"].startswith('[') and settings[group][parameter]["factoryValue"].endswith(']'):
                        settings[group][parameter]["controlType"] = 'multiselect_box'
                    else:
                        settings[group][parameter]["controlType"] = 'select_box'
                elif (settings[group][parameter]["minimumValue"] == '0') and (settings[group][parameter]["maximumValue"] == '1'):
                    settings[group][parameter]["controlType"] = 'checkbox'
                else:
                    try:
                        mi = int(settings[group][parameter]["minimumValue"])
                        ma = int(settings[group][parameter]["maximumValue"])
                        if (ma - mi) < 50:
                            settings[group][parameter]["controlType"] = 'slider'
                    except:
                        pass
                #force text_input on specific parameters
                if f'{group}.{parameter}' in ['CORE.SERIAL','HUB.TYPE']:
                    settings[group][parameter]["controlType"] = 'text_input'
                #convert values based on the controlType (necessary for multiselect_box, checkbox, slider  )
                
                logging.info(settings[group][parameter]["value"])
                if settings[group][parameter]["controlType"] == 'multiselect_box':
                    settings[group][parameter]["factoryValue"] = settings[group][parameter]["factoryValue"].strip('[').strip(']').split(',')
                elif settings[group][parameter]["controlType"] == 'checkbox':
                    settings[group][parameter]["factoryValue"] = bool(int(settings[group][parameter]["factoryValue"]))
                    settings[group][parameter]["minimumValue"] = bool(int(settings[group][parameter]["minimumValue"]))
                    settings[group][parameter]["maximumValue"] = bool(int(settings[group][parameter]["maximumValue"]))
                elif settings[group][parameter]["controlType"] == 'slider':
                    settings[group][parameter]["factoryValue"] = int(settings[group][parameter]["factoryValue"])
                    settings[group][parameter]["minimumValue"] = int(settings[group][parameter]["minimumValue"])
                    settings[group][parameter]["maximumValue"] = int(settings[group][parameter]["maximumValue"])

                #copy.deepcopy() is necessary to avoid references and anchors in the toml file
                settings[group][parameter]["defaultValue"] = copy.deepcopy(settings[group][parameter]["factoryValue"])
                settings[group][parameter]["value"] = copy.deepcopy(settings[group][parameter]["factoryValue"])
                settings[group][parameter]["provisionalValue"] = copy.deepcopy(settings[group][parameter]["factoryValue"])
                logging.info(settings[group][parameter]["controlType"])
                logging.info(settings[group][parameter]["value"])
        logging.info(f"Saving all setting and infos in '{filepath}'")
        with open(filepath,'w') as f:
            toml.dump(settings, f)
            
    def reboot(self):
        logging.info('Rebooting')
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()
        self.connection.readlines(-1)
        self.connection.write('reboot\r\n'.encode('utf_8'))

    @property
    def serial(self):
        return self.get('CORE','SERIAL')

    def set_serial(self, serial='Unknown'):
        self.set('CORE', 'SERIAL', str(serial), superuser=True)
        
    def set_measuring_interval(self, interval):
        self.set('CORE', 'MSI', str(interval))

    def set_measuring_counts_per_send(self, counts):
        self.set('CORE', 'MSC', str(counts))       

    def set_mqtt(self, broker_ip, port='1883', username= '', password= '', client_id= '', lifetime=300, timeout= 15, retries= 4, qos=1, topic=''):
        self.set('HUB', 'TYPE', 'mqtt')
        self.set('HUB', 'TSYNC_WAIT', '1')
        self.set('HUB', 'T_RETRY_MODE', '1')
        self.set('HUB','T_RETRY', '60')
        self.set('HUB', 'T_RETRY_MAX', '43200')
        self.set('HUB', 'LIFETIME',str(lifetime)) 
        self.set('HUB', 'PROTOCOL','tcp')   
        self.set('HUB', 'REMOTE_IP',str(broker_ip))   
        self.set('HUB', 'REMOTE_PORT',str(port))  
        if username:
            self.set('MQTT', 'USER',str(username))  
        if password:
            self.set('MQTT', 'PW',str(password))
        self.set('MQTT', 'TIMEOUT',str(timeout))
        self.set('MQTT', 'MAX_RETRY',str(retries))
        self.set('MQTT', 'QOS',str(qos))
        self.set('MQTT', 'CLIENT_ID',client_id)
        self.set('MQTT', 'TOPIC_UP',topic)
        self.set('MQTT', 'TOPIC_DOWN',f'{topic}/dl')

    def set_topic(self, topic):
        self.set('MQTT', 'TOPIC_UP',topic)
        self.set('MQTT', 'TOPIC_DOWN',f'{topic}/dl')
    
    @property
    def mqtt_interval(self):
        self.get('CORE', 'MSI')

    def set_measuring_interval(self, interval):
        self.set('CORE', 'MSI', str(interval))   

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
        logging.info('Erasing flash... (This may take a while!)')
        return not PS280.run_command_with_realtime_output([sys.executable, "-m", "esptool", "-b", "460800", "erase_flash"])
        
    
    @staticmethod
    def firmware_update(bootloader_file, partition_table_file,firmware_file):
        logging.info('Updating firmware')
        return not PS280.run_command_with_realtime_output( 
            [
                sys.executable, "-m", "esptool", "-b", "460800", "write_flash",
                "0x0000", bootloader_file,
                "0x8000", partition_table_file,
                "0x10000", firmware_file
                ]
            )

def flash_firmware(firmware_version=''):
    bootloader_file= f'firmware/{firmware_version}/bootloader.bin'
    partition_table_file= f'firmware/{firmware_version}/partition-table.bin'
    firmware_file= f'firmware/{firmware_version}/pikk-sense-esp32s3.bin'
    sensor= PS280(timeout=1)
    #sensor.settings(printout= True)
    PS280.firmware_erase()
    logging.info('ERASED')
    time.sleep(5)
    return(PS280.firmware_update(bootloader_file, partition_table_file,firmware_file))
        
def configure_for_udk(firmware_version='', topic='PS-280/udk.playground', baudrate=9600, serial='', measuring_interval=900, measuring_counts_per_send=4, port=''):
    if firmware_version:
        self.flash_firmware(firmware_version)
    sensor= PS280(baudrate= baudrate,timeout=0.5)
    #sensor.reboot()
    time.sleep(1)
    sensor.aural_boot_signal.off()
    sensor.visual_registration_signal.off()
    sensor.visual_boot_signal.off()
    sensor.co2_warning.off()
    sensor.temperature_warning.off()
    sensor.humidity_warning.off()
    sensor.set_measuring_interval(900)
    sensor.set_measuring_counts_per_send(4)
    sensor.set_mqtt(broker_ip= '194.94.110.169', 
                    port='1883', 
                    username= '', 
                    password= '', 
                    client_id= '', 
                    lifetime=300, 
                    timeout= 15, 
                    retries= 4, 
                    qos=1, 
                    topic=topic)
    if serial:
        sensor.set_serial(serial)
    #sensor.reboot()
    time.sleep(10)
    return(sensor.settings())

    def create_defaults(self, filepath= 'firmware_defaults.toml'):
        for group,pset in settings.items():
            for parameter,value in pset.items():
                settings[group][parameter]={"shortDescription":'',
                                            "longDescription":'',
                                            "controlType":'',
                                            "minimum_value":'',
                                            "maximum_value":'',
                                            "allowed_values":'',
                                            "default_value": value}
# -

