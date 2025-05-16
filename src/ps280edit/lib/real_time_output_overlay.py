import sys
import flet as ft
import threading
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO


class RealTimeOutputOverlay(ft.Row):
    """
    A reusable component for displaying real-time function output in an overlay.

    Features:
    - Displays standard output (stdout) in white and standard error (stderr) in red.
    - Allows manual closing of the overlay.
    - Automatically closes the overlay if no errors occur.
    - Keeps the overlay open if any stderr output is detected.
    """

    def __init__(self, page: ft.Page, stdout= sys.stdout, stderr= sys.stderr):
        super().__init__()
        self.page = page
        self.error_occurred = False  # Track if any errors occurred during function execution

        # Output area for displaying stdout and stderr
        self.output_area = ft.ListView(
            expand=True,
            spacing=2,
            auto_scroll=True,
        )

        # Close button
        self.close_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_color="red",
            tooltip="Close",
            on_click=self.close_overlay,
        )

        # Title bar
        self.title_bar = ft.Row(
            [
                ft.Text("Process Output", color="white", expand=True),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Create overlay container
        self.overlay_layout = ft.Container(
            content=ft.Column(
                [self.title_bar, self.output_area],
                spacing=10,
            ),
            bgcolor="black",
            padding=20,
            border_radius=10,
            width=600,
            height=400,
            alignment=ft.alignment.top_center,
            border=ft.border.all(2, "white"),
            visible=False,  # Initially hidden
        )

        # Add the overlay to the page before using it
        self.page.overlay.append(self.overlay_layout)
        self.page.update()  # Ensure UI updates

    def close_overlay(self, e=None):
        """Close the overlay."""
        self.overlay_layout.visible = False
        self.page.update()  # Update the page to reflect changes

    def run_function_with_realtime_output(self, function):
        """
        Run a Python function and display its stdout/stderr in the overlay in real time.

        Args:
            function (callable): The Python function to execute.
        """

        def update_ui(text, is_error=False):
            """Update the UI with new output."""
            self.output_area.controls.append(
                ft.Text(
                    text.strip(),
                    size=12,
                    font_family="monospace",
                    color="red" if is_error else "white",
                )
            )
            if is_error:
                self.error_occurred = True
            self.page.update()

        def process_function():
            """Run the function and redirect its output."""
            stdout_stream = RealTimeOutput(update_ui, is_error=False)
            stderr_stream = RealTimeOutput(update_ui, is_error=True)
            try:
                with redirect_stdout(stdout_stream), redirect_stderr(stderr_stream):
                    function()  # Run the function
                    #time.sleep(2)
                    self.error_occurred= False
            except Exception as e:
                update_ui(f"Error: {e}", is_error=True)
                self.error_occurred = True
            finally:
                # Close overlay only if no errors occurred
                if not self.error_occurred:
                    self.close_overlay()
                    

        # Clear previous output and make the overlay visible
        self.page.add(self) 
        self.output_area.controls.clear()
        self.overlay_layout.visible = True
        self.page.update()
                
        # Run the function in a separate thread
        thread = threading.Thread(target=process_function, daemon=True)
        thread.start()
        thread.join()
        return(not self.error_occurred)
        
class RealTimeOutput:
    """
    A custom stream class to redirect stdout and stderr for real-time updates.

    Args:
        update_callback (function): A function to update the UI with new output lines.
    """

    def __init__(self, update_callback, is_error=False):
        self.buffer = StringIO()
        self.update_callback = update_callback
        self.is_error = is_error

    def write(self, text):
        """Write output to the buffer and update the UI."""
        if text.strip():
            self.buffer.write(text)
            self.update_callback(text, self.is_error)

    def flush(self):
        """Flush the buffer."""
        self.buffer.flush()


# Usage example:
def test_function():
    """A function that generates output."""
    import time
    for i in range(5):
        print(f"Running step {i+1}")
        time.sleep(1)
    print("Done!")


def main(page: ft.Page):
    overlay = RealTimeOutputOverlay(page)

    def start_function(e):
        overlay.run_function_with_realtime_output(test_function)

    page.add(ft.ElevatedButton("Run Process", on_click=start_function))


#ft.app(target=main)