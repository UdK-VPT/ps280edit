"""
real_time_output_overlay.py

Author: Werner Kaul-Gothe
Department: VPT
Organisation: Universität der Künste Berlin IAS
Date: 2025-02-19

Description:
A reusable Flet component for displaying real-time output of Python functions in an overlay.
The overlay displays standard output (stdout) in white and standard error (stderr) in red,
with functionality to close the overlay manually or automatically after execution.
"""
import sys 
import flet as ft
import threading
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
stdoutstream= sys.stdout
stderrstream= sys.stderr


class RealTimeOutputOverlay(ft.Row):
    """
    A reusable component for displaying real-time function output in an overlay.

    Features:
    - Displays standard output (stdout) in white and standard error (stderr) in red.
    - Allows manual closing of the overlay.
    - Automatically closes the overlay if no errors occur.
    - Keeps the overlay open if any stderr output is detected.
    - Styled to resemble a window with a title bar and close button.
    """

    def __init__(self, stdout= sys.stdout, stderr= sys.stderr):
        """Initialize the overlay with its layout and components."""
        self.bu_stdout= sys.stdout
        self.stdout= stdout
        self.bu_stderr= sys.stderr
        self.stderr= stderr
        super().__init__()
        self.error_occurred = False  # Track if any errors occurred during function execution

        # Output area for displaying stdout and stderr
        self.output_area = ft.ListView(
            padding=0,
            spacing=0,
            #scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            auto_scroll= True
            #horizontal_alignment=ft.CrossAxisAlignment.START,  # Align text to the left
        )

        # Close button styled as a top-left button in the title bar
        self.close_button = ft.ElevatedButton(
            "✖",
            on_click=self.close_overlay,
            bgcolor=ft.colors.TRANSPARENT,
            color=ft.colors.RED,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=ft.Padding(2, 4, 2, 4),
            ),
        )

        # Title bar for the "window"
        self.title_bar = ft.Row(
            [
                ft.Text("Process Output", color="white", expand=True),#, height=0.8),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Create the overlay layout (initially not visible)
        self.overlay_layout = ft.Container(
            visible=False,  # Initially invisible
            content=ft.Column(
                [
                    self.title_bar,  # Add the title bar to mimic a window
                    self.output_area,
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor="black",  # Black background for the overlay
            border_radius=10,
            width=600,
            height=400,
            alignment=ft.alignment.top_center,
            border=ft.Border(
                top=ft.BorderSide(2, ft.colors.WHITE),
                bottom=ft.BorderSide(2, ft.colors.WHITE),
                left=ft.BorderSide(2, ft.colors.WHITE),
                right=ft.BorderSide(2, ft.colors.WHITE),
            ),
        )

    def build(self):
        """
        Build the overlay layout for use in Flet.

        Returns:
            ft.Container: The overlay container component.
        """
        return self.overlay_layout

    def close_overlay(self, e=None):
        """
        Close the overlay.

        Args:
            e: The event triggering the closure (default: None).
        """
        self.overlay_layout.visible = False
        self.update()

    def run_function_with_realtime_output(self, function):
        """
        Run a Python function and display its stdout/stderr in the overlay in real time.

        Args:
            function (callable): The Python function to execute.
        """
        def update_ui(text, is_error=False):
            """
            Callback to update the UI with new output.

            Args:
                text (str): The output text to display.
                is_error (bool): Whether the output is an error (stderr).
            """
            self.output_area.controls.append(
                ft.Text(
                    text.strip(),
                    size=12,
                    #height= 0.8,
                    font_family="monospace",
                    color="red" if is_error else "white",  # Red for errors, white for stdout
                )
            )
            if is_error:
                mark_error_occurred()
            self.update()

        def mark_error_occurred():
            """Mark that an error occurred to keep the overlay open."""
            self.error_occurred = True

        def process_function():
            """Run the function and redirect its output."""
             
           # caller_stdout = self.stdout   # Save the caller's stdout
           # caller_stderr = self.stderr  # Save the caller's stderr

            def wrapped_function():
                # Redirect sys.stdout globally to the caller's stdout
                sys.stdout = self.stdout
                sys.stderr = self.stderr 
                stdout_stream = RealTimeOutput(
                    update_callback=lambda text, _: update_ui(text, is_error=False)  # Ignore the second argument
                )
                stderr_stream = RealTimeOutput(
                    update_callback=lambda text, _: update_ui(text, is_error=True)  # Ignore the second argument
                )
                # Start the thread
                
                try:
                    with redirect_stdout(stdout_stream), redirect_stderr(stderr_stream):
                        result= function()   # Run the worker function
                finally:
                    # Restore original stdout
                    sys.stdout = self.bu_stdout
                    sys.stderr = self.bu_stderr
                return(result)
                
            # Correctly handle stdout and stderr streams
            stdout_stream = RealTimeOutput(
                update_callback=lambda text, _: update_ui(text, is_error=False)  # Ignore the second argument
            )
            stderr_stream = RealTimeOutput(
                update_callback=lambda text, _: update_ui(text, is_error=True)  # Ignore the second argument
            )

                # Start the thread
            self.error_occurred = False  # Reset error state    
            try:
                with redirect_stdout(stdout_stream), redirect_stderr(stderr_stream):
                    result= wrapped_function()  # Call the provided function
            except Exception as e:
                # Display exception details and mark the error
                update_ui(f"Error: {e}", is_error=True)
                self.error_occurred = True
            finally:
                # Only close the overlay if no errors occurred
                if not self.error_occurred:
                    self.close_overlay()
           # print(self.error_occurred)
        # Clear previous output and ensure the overlay is visible
        self.output_area.controls.clear()
        self.overlay_layout.visible = True  # Make the overlay visible
        self.update()

        # Run the function in a separate thread
        thread= threading.Thread(target=process_function, daemon=True)
        thread.start()
        thread.join()
        return(not self.error_occurred)
        
class RealTimeOutput:
    """
    A custom stream class to redirect stdout and stderr for real-time updates.

    Args:
        update_callback (function): A function to update the UI with new output lines.
        error_callback (function, optional): A function to notify when an error occurs.
    """

    def __init__(self, update_callback, error_callback=None, stderr= sys.stderr, stdout= sys.stdout):
        self.buffer = StringIO()
        self.update_callback = update_callback
        self.error_callback = error_callback
        self.bu_stdout= sys.stdout
        self.stdout= stdout
        self.bu_stderr= sys.stderr
        self.stderr= stderr
        
    def write(self, text, is_error=False):
        """
        Write output to the buffer and update the UI.

        Args:
            text (str): The output text to write.
            is_error (bool): Whether the output is an error (stderr).
        """
        if text.strip():  # Ignore empty lines
            self.buffer.write(text)
            self.update_callback(text, is_error)  # Pass both arguments
            if is_error and self.error_callback:
                self.error_callback()  # Trigger error callback

    def flush(self):
        """Flush the buffer (required for some environments)."""
        self.buffer.flush()