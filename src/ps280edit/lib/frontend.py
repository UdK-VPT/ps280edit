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

# + editable=true slideshow={"slide_type": ""}
import sys, os
#TOOLBOXROOT= os .path.join(os.path.abspath("../.."),'src')
#if TOOLBOXROOT not in sys.path:
#
#    sys.path = [TOOLBOXROOT]+sys.path
#
from .ps280_toolbox import PS280#, flash_firmware, configure_for_udk

#STICKERTOOLPATH= os.path.join(os.path.dirname(os.getcwd()),'stickertool')
#if STICKERTOOLPATH not in sys.path:
#    sys.path= [STICKERTOOLPATH]+sys.path

from .stickertool import Sticker
import flet as ft
import toml
from .backend import PS280EditorBackend
from .real_time_output_overlay import RealTimeOutputOverlay
from .custom_elements import LabeledText, LabeledTextfield, Button, LabeledDropdown, LabeledContainer, Label
import copy
stdoutstream= sys.stdout
stderrstream= sys.stderr
class PS280EditorUI:
    """Handles the user interface for the TOML Editor application."""

    def __init__(self, backend: PS280EditorBackend): 
        self.backend = backend  # Inject the backend instance

    def create_elements(self, page, output_overlay):
        self.texts= {
            'database_root': LabeledText(
                page= page, 
                labeltext="Root Directory", 
                value=self.backend.database_name
                ),
            'path_as_topic' : LabeledText(
                page= page,
                labeltext="Configuration Record", 
                value=self.backend.path_as_topic
                ),
            'mqtt_broker' : LabeledText(
                page= page,
                labeltext="MQTT Broker IP", 
                value=self.backend.path_as_topic
                ),
            }

        self.textfields={
            'topic': LabeledTextfield(
                page= page, 
                labeltext= 'MQTT Topic', 
                on_blur=lambda _: self.on_set_configuration_topics(page)
            ),
            'serial': LabeledTextfield(
                page= page, 
                labeltext= 'Serial Number', 
                on_blur=lambda _: self.on_set_configuration_serial(page)
            ),
            'mqtt_broker': LabeledTextfield(
                page= page, 
                labeltext= 'MQTT Broker IP', 
                on_blur=lambda _: self.on_set_configuration_mqtt_broker(page)
            ),
            }

        

        self.buttons= {
            'connect' : Button(
                page= page,
                labeltext= "Connect", 
                callback= lambda _: self.on_connect(page, output_overlay)
                ),
            'read' : Button(
                page= page,
                labeltext= "Read",  
                callback= lambda _: self.on_read_settings(page, output_overlay)
                ),
            'write' : Button(
                page= page,
                labeltext= "Write",  
                callback= lambda _: self.on_write_settings(page, output_overlay)
                ),
            'set_from_template' : Button(
                page= page,
                labeltext= "Set",  
                callback= lambda _: self.on_set_from_template(page, output_overlay)
                ),
            'load' : Button(
                page= page,
                labeltext= "Load",  
                callback= lambda _: self.selectors['config_file'].pick_files(allowed_extensions=["toml"], 
                                                                             initial_directory=self.backend.database_root,
                                                                             dialog_title="Choose the configuration file")
                ),
            'erase_firmware' : Button(
                page= page,
                labeltext= "Erase",  
                callback= lambda _: self.on_firmware_erase(page, output_overlay)
                ),
            'flash_firmware' : Button(
                page= page,
                labeltext= "Flash",  
                callback= lambda _: self.on_firmware_update(page, output_overlay)
                ),
            'set_path_to_topic' : Button(
                page= page,
                labeltext= "From topic", 
                callback= lambda _: self.on_set_file_path_to_topic(page)
                ),
            'set_topic' : Button(
                page= page,
                labeltext= "Set topics",  
                callback= lambda _: self.on_set_configuration_topics(page)
                ),
            'save' : Button(
                page= page,
                labeltext= "Save",  
                callback= lambda _: self.on_save_file(page)
                ),
            'save_as' : Button(
                page= page,
                labeltext= "Saveas",  
                callback= lambda _: self.on_save_file(page)
                ),
            'set_database_root' : Button(
                page= page,
                labeltext= "Select",   
                callback= lambda _: self.selectors['database_root'].get_directory_path(initial_directory=self.backend.database_root,
                                                                                       dialog_title="Choose the database root directory")
                ),
           'create_sticker' : Button(
                page= page,
                labeltext= "Create Sticker",   
                callback= lambda _: self.backend.create_stickers()
                ),
            }
    
        self.selectors= {
                'database_root': ft.FilePicker(
                    on_result= lambda e: self.on_database_root_selected(e, page)
                    ),
                'config_file' : copy.deepcopy(ft.FilePicker)(
                    on_result= lambda e: self.on_config_file_selected(e, page)
                    ),
                'template_file' : copy.deepcopy(ft.FilePicker)(
                    on_result= lambda e: self.on_template_file_selected(e, page),
                    ),
                }


            
        self.dropdowns = {
            'firmware' : LabeledDropdown(
                page= page,
                labeltext= "Firmware Version",
                options= [ft.dropdown.Option(tpl) for tpl in self.backend.firmware_versions],
                defaultoption= sorted(self.backend.firmware_versions)[0],
                callback= lambda _: self.on_set_firmware_version(page)
                ),
            'template' : LabeledDropdown(
                page= page,
                labeltext= "Configuration Template",
                options= [ft.dropdown.Option(tpl) for tpl in self.backend.templates],
                defaultoption= sorted(self.backend.templates)[-1],
                callback= self.backend.set_template
                ),
            }



                       # height=20,
                      #  )
        self.forms= {
            'form' : ft.Column(
                #spacing=20, 
                scroll=ft.ScrollMode.ALWAYS, 
                expand=True
                )
            }

                
        self.widgets= {
            'configuration_form': LabeledContainer(
                page= page,
                labeltext= "Configuration Details",  # The label
                col= {"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},   
                controls=
                    [       
                    self.forms['form']
                    ],
            ),
            'basic': LabeledContainer(
                page= page,
                labeltext= "Basic Settings",  # The label
                controls=
                    [       
                         self.dropdowns['firmware'],
                        
                        ft.ResponsiveRow(
                            [
                                self.buttons['connect'],               
                                self.buttons['erase_firmware'],
                                self.buttons['flash_firmware']
                            ],
                            alignment= ft.MainAxisAlignment.END
                         ),
                        self.textfields['serial'],
                        self.textfields['mqtt_broker'],
                        self.textfields['topic'],
                        ft.ResponsiveRow(
                            [
                                self.buttons['create_sticker'],
                    
                                #self.buttons['set_path_to_topic']
                            ],
                            alignment= ft.MainAxisAlignment.END
                            #run_spacing=10,
                            #alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                height=360,
            ),
           'database': LabeledContainer(
                page= page,
                labeltext= "Database",  # The label
                controls=
                    [       
                    self.texts['database_root'],
                    ft.ResponsiveRow(
                        controls= 
                            [
                                self.buttons['set_database_root'],
                            ],
                        alignment= ft.MainAxisAlignment.END
                    ),
                    self.dropdowns['template'],
                    ft.ResponsiveRow(
                            [
                                self.buttons['set_from_template'],                
                            ],
                            alignment= ft.MainAxisAlignment.END
                            #run_spacing=10,
                            #alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    self.texts['path_as_topic'],
                    ft.ResponsiveRow(
                        controls= 
                            [
                                self.buttons['set_path_to_topic'],
                                 self.buttons['load'],                
                                self.buttons['save'],
                            ],
                        alignment= ft.MainAxisAlignment.END
                    ),    
                     Label(page, "Configuration PS-280"),
                        ft.ResponsiveRow(
                            [
                                self.buttons['connect'],                
                                self.buttons['read'],
                                self.buttons['write'],
                            ],
                            alignment= ft.MainAxisAlignment.END,
                            #run_spacing=10,
                            #alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),

                    ],
               height=360,
            ),
       }

        self.pagecomponents= {
            'header': ft.ResponsiveRow(
                [
                    ft.Text("PS-280 Configuration Tool", style=ft.TextThemeStyle.TITLE_LARGE),
                    self.widgets['database'],
                    self.widgets['basic'],
                    #self.widgets['local'],
                    ],
                
                ),
            'forms': ft.ResponsiveRow(
                [
                   self.widgets['configuration_form'],
                    ],
                ), 
            
            }
        
            
    
    def update_ui(self, page):
        """Updates static UI components like database name and path."""
        self.texts['database_root'].value = self.backend.database_name
        self.texts['path_as_topic'].value = self.backend.path_as_topic
        section,key= self.backend.topic_upload.split('.')
        try:
            self.textfields['topic'].value= self.backend.toml_data[section][key]
        except:
            pass
        self.texts['database_root'].update()
        self.textfields['topic'].update()
        self.texts['path_as_topic'].update()
        page.update()
        self.render_form(page)
        #print(self.backend.toml_data)

    def render_form(self, page):
        """Dynamically creates and updates the form container with expandable panels."""
        self.forms['form'].controls.clear()

        def create_row(key, value, section=None):
            return ft.Row([
                ft.Text(key, 
                        width=150,
                        height=20,
                        size=12),
                ft.TextField(
                    value=str(value),
                    expand=True,
                    label= "",
                    border_width=0,
                    text_style= ft.TextStyle(size= 13),
                    content_padding=ft.Padding(10, 5, 10, 5),
                    bgcolor= page.theme.color_scheme.secondary,
                    height=20,
                    on_change=lambda e: self.backend.update_toml_data(section, key, e.control.value),
                ),
            ])

        panels = []
        for section, values in self.backend.toml_data.items():
            if isinstance(values, dict):  # Nested section
                rows = [create_row(key, value, section) for key, value in values.items()]
                panels.append(
                    ft.ExpansionPanel(
                        header=ft.Text(f"[{section}]"),
                        content=ft.Column(controls=rows),
                        expanded=False,
                        height=20
                    )
                )
            else:  # Top-level key-value pairs
                self.forms['form'].controls.append(create_row(section, values))

        if panels:
            self.forms['form'].controls.append(ft.ExpansionPanelList(controls=panels))

        self.forms['form'].update()


    def sync_firmware_dropdown(self, page):
        active_fw= [tpl for tpl in self.backend.firmware_versions if  self.backend.firmware_version.startswith(tpl)]
        if active_fw:
            self.dropdowns['firmware'].value = active_fw[0]
        
    def on_write_settings(self, page, output_overlay):
        
        if output_overlay.run_function_with_realtime_output(self.backend.write_configuration):
            self.show_snackbar(page, "Successfully wrote settings to PS-280!")
        else:
            self.show_snackbar(page, "Error writing settings to PS-280!")

        
        
    def on_set_from_template(self, page, output_overlay):
        if output_overlay.run_function_with_realtime_output(lambda : self.backend.update_configuration_from_template(self.dropdowns['template'].value)):
            self.show_snackbar(page, f"Updated configuration from template {self.dropdowns['template'].value}!")
        else:
            self.show_snackbar(page, f"Could not update configuration from template {self.dropdowns['template'].value}!")
        self.update_ui(page)
        #self.render_form()


    def on_set_configuration_topics(self, page):
            success, message = self.backend.set_configuration_topics(self.textfields['topic'].value)
            self.update_ui(page)
            if success:
                #self.render_form()  # Render the form based on the loaded TOML data
                self.show_snackbar(page, message)
            else:
                self.show_snackbar(page, f"Set topics in configuration to {self.dropdowns['template'].value}")

    def on_set_configuration_serial(self, page):
            success, message = self.backend.set_configuration_serial(self.textfields['serial'].value)
            self.update_ui(page)
            if success:
                #self.render_form()  # Render the form based on the loaded TOML data
                self.show_snackbar(page, message)
            else:
                self.show_snackbar(page, f"Set serial number in configuration to {self.textfields['serial'].value}")
            success, message = self.backend.set_configuration_client_id(self.textfields['serial'].value)
            self.update_ui(page)
            if success:
                #self.render_form()  # Render the form based on the loaded TOML data
                self.show_snackbar(page, message)
            else:
                self.show_snackbar(page, f"Set MQTT Client ID in configuration to {self.textfields['serial'].value}")
                

    def on_set_configuration_mqtt_broker(self, page):
            success, message = self.backend.set_configuration_mqtt_broker_ip(self.textfields['mqtt_broker'].value)
            self.update_ui(page)
            if success:
                #self.render_form()  # Render the form based on the loaded TOML data
                self.show_snackbar(page, message)
            else:
                self.show_snackbar(page, f"Set MQTT broker in configuration to {self.textfields['mqtt_broker'].value}")
    #Erase Firmware
    def on_firmware_erase(self, page, output_overlay):
        
        if output_overlay.run_function_with_realtime_output(self.backend.firmware_erase):
            self.show_snackbar(page, "Successfully erased firmware on PS-280!")
        else:
            self.show_snackbar(page, "Error on erasing firmware from PS-280!") 

    #Erase Firmware
    def on_firmware_update(self, page, output_overlay):
        
        if output_overlay.run_function_with_realtime_output(self.backend.firmware_flash):
            self.show_snackbar(page, f"Successfully updated firmware to {self.dropdowns['firmware'].value}! ")
        else:
            self.show_snackbar(page, f"Error on updating firmware fto {self.dropdowns['firmware'].value}!")
 
    #Connect    
    def on_connect(self, page, output_overlay):
        
        if output_overlay.run_function_with_realtime_output(self.backend.connect):
            self.show_snackbar(page, "Successfully connected to PS-280!")
        else:
            self.show_snackbar(page, "No connection to PS-280!")
            
         
    #read settings from device
    def on_read_settings(self, page, output_overlay):
        
        if output_overlay.run_function_with_realtime_output(self.backend.read_settings):
            self.textfields['topic'].value= self.backend.path_as_topic
            self.textfields['serial'].value= self.backend.serial_number
            self.textfields['mqtt_broker'].value= self.backend.mqtt_broker_ip
            self.sync_firmware_dropdown(page)
            self.update_ui(page)
            #self.render_form()
            self.show_snackbar(page, "Settings successfully read from PS-280!")
        else:
            self.show_snackbar(page, "Error reading settings from PS-280d!")

    def on_set_firmware_version(self, page):
        
        if self.backend.set_firmware_version(self.dropdowns['firmware'].value):
            self.update_ui(page)
            #self.render_form()
            self.show_snackbar(page, "Settings successfully read from PS-280!")
        else:
            self.show_snackbar(page, "Error reading settings from PS-280d!")


    def on_file_folderselect(e, page):
        pass
    #load settings from file
    def on_config_file_selected(self, result, page):
        """Handles file selection and updates the UI."""
        if result.files:
            success, message = self.backend.load_toml_file(result.files[0].path)
            #self.textfields['topic'].value= self.backend.toml
            self.texts['path_as_topic'].value=  self.backend.path_as_topic
            self.textfields['topic'].value= self.backend.path_as_topic
            self.textfields['serial'].value= self.backend.serial_number
            self.textfields['mqtt_broker'].value= self.backend.mqtt_broker_ip
            self.sync_firmware_dropdown(page)
            self.update_ui(page)
            self.show_snackbar(page, message)


    def on_database_root_selected(self, result, page):
        """Handles directory selection and updates the UI."""
        if result.path:
            self.backend.database_root = result.path
            self.update_ui(page)
            self.show_snackbar(page, "Database root set successfully!")

                
    def on_save_file(self, page):
        """Handles saving the TOML file."""
        success, message = self.backend.save_toml_file()
        self.show_snackbar(page, message)

    def on_set_file_path_to_topic(self, page):
        """Handles saving the TOML file."""
        message = self.backend.set_file_path_to_topic()
        self.update_ui(page)
        self.show_snackbar(page, message)

        
    def show_snackbar(self, page, message):
        """Displays a snackbar with a message."""
        page.overlay.append(ft.SnackBar(ft.Text(message), open=True))
        page.update()

    def main(self, page= ft.Page):
        """Main function to initialize the app."""
        page.title = "TOML Editor"
        page.window_width = 800
        page.window_height = 1000
        page.scroll=ft.ScrollMode.ALWAYS
            # Define a custom theme with a primary color
        custom_theme = ft.Theme(
            
           color_scheme=ft.ColorScheme(
            #    primary=page.theme.color_scheme.secondary_container,

           # secondary=ft.colors.ORANGE,
                #primary=ft.colors.GREY_400,  # Set the primary color explicitly
                secondary=ft.colors.GREY_600,
                secondary_container= ft.colors.GREY_800,# (Light Lavender)

            )
        )
        page.theme = custom_theme  # Assign the custom theme to the page
        
        output_overlay = RealTimeOutputOverlay(page=page, stdout= stdoutstream, stderr= stderrstream)
        page.overlay.append(output_overlay)
        self.create_elements(page, output_overlay)
        
        page.overlay.append(self.selectors['database_root'])
        page.overlay.append(self.selectors['config_file'])
        
        # Add components to the page
        page.add(self.pagecomponents['header'])
        page.add(self.pagecomponents['forms'])
        #page.add(self.widgets['configuration_form'])
        self.backend.set_firmware_version(self.dropdowns['firmware'].value)
        #output_overlay.overlay_layout.visible = True
        
        
        
## Start the application
#if __name__ == "__main__":
#
#    DATABASE_ROOT= os.path.abspath('../configuration/cfg/config')
#    FIRMWARE_DIR= os.path.abspath('../configuration/firmware')
#    TEMPLATE_DIR= os.path.abspath('../configuration/cfg/config/templates')
#    STICKER_CONFIG_FILE=os.path.abspath('../stickertool/cfg/stickertool.yaml')
#    STICKER_TEMPLATE_FILE= os.path.abspath('../stickertool/cfg/templates/udk_vpt_emu_na.png')
#    PARAMETERS_SUPERUSER= ["CORE.SERIAL", "OTA.RESULT", "RUNTIME.IPV4", "RUNTIME.RSSI"]
#    PARAMETERS_IGNORE= ["CORE.VERSION"]
#    
#    backend = PS280EditorBackend(database_root= DATABASE_ROOT, 
#                                firmware_dir= FIRMWARE_DIR, 
#                                template_dir= TEMPLATE_DIR,
#                                sticker_config_file= STICKER_CONFIG_FILE,
#                                sticker_template_file= STICKER_TEMPLATE_FILE,
#                                parameters_ignore= PARAMETERS_IGNORE,
#                                parameters_superuser= PARAMETERS_SUPERUSER
#                               )
#    ui = PS280EditorUI(backend=backend)  
#    ft.app(target=ui.main)
#    #backend.connect()
    #backend.set('CORE','SERIAL','123',True)

# + editable=true slideshow={"slide_type": ""}



# + editable=true slideshow={"slide_type": ""}

# -




