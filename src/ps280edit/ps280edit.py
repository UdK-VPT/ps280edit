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
"""""
Author: Werner Kaul-Gothe
Department: VPT
Organization: Universit\u00e4t der K\u00fcnste Berlin IAS
Date: [Current Date]

Description:
This script initializes and runs the SP280Edit application. It loads configurations,
creates necessary directories, copies default files if needed, and starts the user interface.

Dependencies:
- os
- flet
- yaml
- shutil
- platformdirs
- lib.backend (PS280EditorBackend) 
- lib.frontend (PS280EditorUI)
"""

import os,sys
import flet as ft
import yaml
import shutil
import platformdirs
from lib.backend import PS280EditorBackend
from lib.frontend import PS280EditorUI

def get_yaml_path(name):
    """Finds the correct path to ps280edit.yaml, whether running as a script or a PyInstaller EXE."""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS  # Temp directory where PyInstaller extracts files
    else:
        # Running as a normal script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, name)

yaml_path = get_yaml_path( "ps280edit.yaml")

with open(yaml_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

## Load configuration from YAML file
#with open("ps280Edit.yaml", "r", encoding="utf-8") as file:
#    config = yaml.safe_load(file)

print(config)

# Define working and default directories
DIRS = {
    'databaseroot': {
        'workdir': os.path.abspath(os.path.join(platformdirs.user_documents_dir(), config['app_name'], config['database']['root'])),
        'default': os.path.abspath(os.path.join(get_yaml_path(config['defaults']), config['database']['root'])),
    },
    'firmware_dir': {
        'workdir': os.path.abspath(os.path.join(platformdirs.user_documents_dir(), config['app_name'], config['firmwares'])),
        'default': os.path.abspath(os.path.join(get_yaml_path(config['defaults']), config['firmwares'])),
    },
    'template_dir': {
        'workdir': os.path.abspath(os.path.join(platformdirs.user_documents_dir(), config['app_name'], config['templates'])),
        'default': os.path.abspath(os.path.join(get_yaml_path(config['defaults']), config['templates'])),
    },
    'stickertool': {
        'workdir': os.path.abspath(os.path.join(platformdirs.user_documents_dir(), config['app_name'], config['stickertool']['root'])),
        'default': os.path.abspath(os.path.join(get_yaml_path(config['defaults']), config['stickertool']['root'])),
    },
    'stickertool_templates': {
        'workdir': os.path.abspath(os.path.join(platformdirs.user_documents_dir(), config['app_name'], config['stickertool']['root'],config['stickertool']['templates'])),
        'default': os.path.abspath(os.path.join(get_yaml_path(config['defaults']), config['stickertool']['root'], config['stickertool']['templates'])),
    },
}

# Define files for stickertool
FILES = {
    'stickertool_config': os.path.join(DIRS['stickertool']['workdir'], config['stickertool']['config']),
    'stickertool_template': os.path.join(DIRS['stickertool_templates']['workdir'], config['stickertool']['active_template']),
}


# Ensure all directories exist and copy default files if necessary
for d in DIRS.values():
    print(d['workdir'])
    if not os.path.exists(d['workdir']):
        shutil.copytree(d['default'], d['workdir'], ignore=shutil.ignore_patterns('*.tmp', '*.log'))
        
print(f"\\n\\nSTICKER{FILES['stickertool_config']}\\n\\n")
# Initialize backend
backend = PS280EditorBackend(
    database_root=DIRS['databaseroot']['workdir'],
    firmware_dir=DIRS['firmware_dir']['workdir'],
    template_dir=DIRS['template_dir']['workdir'],
    sticker_config_file=FILES['stickertool_config'],
    sticker_template_file=FILES['stickertool_template'],
    parameters_ignore=config['ps280']['ignore'],
    parameters_superuser=config['ps280']['superuser'],
)

# Initialize UI and start application
ui = PS280EditorUI(backend=backend)
ft.app(target=ui.main)
# -
# !python ps280edit.py









# !python popup.py

# !python lib/real_time_output_overlay.py

dfaf28bb9e6f7DE7a753
