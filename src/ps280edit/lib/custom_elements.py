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
custom_elements.py

Author: Werner Kaul-Gothe
Department: VPT
Organisation: Universität der Künste Berlin IAS
Date: 2025-02-19

Description:
This module defines custom UI components for the PS280Editor applications, including labeled dropdowns,
text fields, buttons, and containers. These components provide consistent styling and
functionality across the user interface.

"""

import flet as ft


import flet as ft

import flet as ft


class LabeledDropdown(ft.Column):
    """
    A labeled dropdown component.
    """
    
    def __init__(self, page, labeltext, options, defaultoption, callback):
        """
        Initialize the labeled dropdown.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The label text for the dropdown.
            options (list): List of options for the dropdown.
            defaultoption: The default selected option.
            callback: Function to call on selection change.
        """
        self.dropdown = ft.Dropdown(
            expand=True,
            options=options,
            value=defaultoption,
            border_width=0,
            hint_style=ft.TextStyle(size=13),
            text_style=ft.TextStyle(size=13),
            bgcolor=page.theme.color_scheme.secondary_container,  # Background color
            #border_color=ft.colors.RED_500,  # Border color
            #bgcolor=ft.colors.LIGHT_BLUE_100, 
            #content_padding= ft.Padding(10, -15, 10, 5),
            on_change=callback,
            dense=True
        )
        
        super().__init__(spacing=3, 
                         #height=45,
                         #alignment=ft.MainAxisAlignment.CENTER,  # 
                         controls=[
            Label(page, labeltext),
            ft.Container(
                expand=True,
                bgcolor=  page.theme.color_scheme.secondary_container,
                content= self.dropdown ,
               #height=40,  # Set fixed height
               #x clip_behavior=ft.ClipBehavior.HARD_EDGE,
                width=float("inf"),
                padding= ft.Padding(10, 0, 10, 0),
                #alignment=ft.MainAxisAlignment.START,

                #alignment=ft.alignment.center,  #
                #padding=ft.padding.all(0),
                border_radius=8,
                #width="100%",
                )
        ])
    
    @property
    def value(self):
        """Get the selected dropdown value."""
        return self.dropdown.value
    
    @value.setter
    def value(self, value):
        """Set the selected dropdown value."""
        self.dropdown.value = value

class Label(ft.Text):
    """
    A simple text label component.
    """
    
    def __init__(self, page, labeltext, size=10, height=14):
        """
        Initialize the label.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The text to display.
            size (int): Font size of the text.
            height (int): Height of the text element.
        """
        super().__init__(
            labeltext,
            size=size,
            color=page.theme.color_scheme.primary,
            height=height
        )

class Button(ft.FilledTonalButton):
    """
    A standard button component.
    """
    
    def __init__(self, page, labeltext, callback, col=None):
        """
        Initialize the button.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The button text.
            callback: Function to call on click.
            col (dict, optional): Column properties for responsive layout.
        """
        if col is None:
            col = {"xs": 6, "sm": 4, "md": 4, "lg": 3, "xl": 3}
        
        super().__init__(
            labeltext,
            height=30,
            width=100,
            #bgcolor= page.theme.color_scheme.secondary_container,

            col=col,
            on_click=callback
        )

class LabeledText(ft.Column):
    """
    A labeled text display component.
    """
    
    def __init__(self, page, labeltext, value):
        """
        Initialize the labeled text display.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The label text.
            value: The text value to display.
        """
        self.text = ft.Text(
            value=value,
            size=12,
            height=20
        )
        
        super().__init__(spacing=3, controls=[
            Label(page, labeltext),
            self.text,
        ])
    
    @property
    def value(self):
        """Get the text value."""
        return self.text.value
    
    @value.setter
    def value(self, value):
        """Set the text value."""
        self.text.value = value

class LabeledTextfield(ft.Column):
    """
    A labeled text input field component.
    """
    
    def __init__(self, page, labeltext, on_blur=None):
        """
        Initialize the labeled text field.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The label text.
            on_blur: Function to call when the field loses focus.
        """
        self.textfield = ft.TextField(
            label="",
            border_width=0,
            text_style=ft.TextStyle(size=13),
            content_padding=ft.Padding(10, 5, 10, 5),
            bgcolor= page.theme.color_scheme.secondary_container,
            on_blur=on_blur,
            height=38
        )
        
        super().__init__(spacing=3, controls=[
            Label(page, labeltext),
            self.textfield,
        ])
    
    @property
    def value(self):
        """Get the text field value."""
        return self.textfield.value
    
    @value.setter
    def value(self, value):
        """Set the text field value."""
        self.textfield.value = value

class LabeledContainer(ft.Column):
    """
    A labeled container component.
    """
    
    def __init__(self, page, labeltext, controls, width='50%', height=None, col=None):
        """
        Initialize the labeled container.
        
        Args:
            page: The Flet page instance.
            labeltext (str): The label text.
            controls (list): List of controls to include in the container.
            width (str, optional): The width of the container.
            height (optional): The height of the container.
            col (dict, optional): Column properties for responsive layout.
        """
        if col is None:
            col = {"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}
        
        self.container = ft.Container(
            expand=True,
            content=ft.ResponsiveRow(controls),
            padding=10,
            border=ft.border.all(1, page.theme.color_scheme.primary),
            border_radius=5,
            width=width,
            height=height
        )
        
        super().__init__(spacing=5, controls=[
            Label(page, labeltext),
            self.container
        ], width=width, col=col, expand=True,)

# -









