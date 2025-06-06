"""
GPSE Strategy Runner - GUI Application
A simple desktop application for running GPSE analysis
"""

import flet as ft
import subprocess
import sys
import os
import threading
import platform


def execute_crew_in_thread():
    """Worker function that runs the subprocess and returns the status message"""
    try:
        # Run the main_crew.py script
        result = subprocess.run(
            [sys.executable, 'main_crew.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Handle any encoding issues
        )
        
        # Check if the process was successful
        if result.returncode == 0:
            # Extract the last non-empty line from stdout (the file path)
            output_lines = result.stdout.strip().split('\n')
            # Get the last non-empty line
            file_path = None
            for line in reversed(output_lines):
                line_stripped = line.strip()
                if line_stripped:
                    # Check if this line looks like a file path
                    if 'strategy_analyses' in line_stripped and line_stripped.endswith('.md'):
                        file_path = line_stripped
                    break
            
            if file_path and os.path.exists(file_path):
                return f'Analysis Complete! Output saved to:\n{file_path}'
            else:
                # Fallback: look for the most recent file in strategy_analyses
                import glob
                files = glob.glob('strategy_analyses/*.md')
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    file_path = os.path.abspath(latest_file)
                    return f'Analysis Complete! Output saved to:\n{file_path}'
                else:
                    return 'Analysis Complete! (Check strategy_analyses folder for output)'
        else:
            # Error occurred
            error_msg = result.stderr if result.stderr else 'Unknown error'
            # Truncate error message if too long
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + '...'
            return f'Error: {error_msg}'
            
    except Exception as ex:
        # Handle any exceptions during subprocess execution
        return f'Error: {str(ex)}'


def main(page: ft.Page):
    """Main function for the GPSE Strategy Runner GUI"""
    
    # Set page properties
    page.title = 'GPSE Strategy Runner'
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 700
    page.window_height = 500
    
    # Store the file path for the open button
    page.output_file_path = None
    
    # Create status display text (accessible via closure)
    status_display = ft.Text(
        'Status: Ready',
        size=16,
        text_align=ft.TextAlign.CENTER,
        selectable=True  # Make text selectable for copying
    )
    
    # Define function to open generated file
    def open_generated_file(e):
        """Open the generated file using the system's default application"""
        file_path_from_stdout = page.output_file_path
        
        if file_path_from_stdout and os.path.exists(file_path_from_stdout):
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(file_path_from_stdout)
                elif system == "Darwin":  # macOS
                    subprocess.call(['open', file_path_from_stdout])
                else:  # Linux and other Unix-like systems
                    subprocess.call(['xdg-open', file_path_from_stdout])
                status_display.value = f'Opened file: {file_path_from_stdout}'
                status_display.update()
            except Exception as ex:
                status_display.value = f'Error opening file: {str(ex)}'
                status_display.update()
        else:
            status_display.value = 'Error: Output file path not found or file does not exist'
            status_display.update()
    
    # Define function to update UI with result
    def update_ui_with_result(message):
        """Update the UI with the result message"""
        status_display.value = message
        status_display.update()
        # Re-enable the button
        run_button.disabled = False
        run_button.update()
        
        # Check if we have a valid file path in the message
        if 'Output saved to:' in message and '\n' in message:
            # Extract the file path from the message
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if 'Output saved to:' in line and i + 1 < len(lines):
                    file_path = lines[i + 1].strip()
                    if os.path.exists(file_path):
                        page.output_file_path = file_path
                        open_file_button.disabled = False
                        open_file_button.update()
                        break
    
    # Define the button click handler
    def start_gpse_analysis(e):
        """Handle the button click event"""
        print('Analysis button clicked...')
        
        # Disable the button to prevent multiple clicks
        run_button.disabled = True
        
        # Update status to show processing
        status_display.value = 'Status: Processing GPSE Analysis... Please wait.'
        status_display.update()
        
        # Define the thread target wrapper
        def thread_target_wrapper():
            """Wrapper function that runs in the thread"""
            # Execute the crew analysis and get the result message
            message_from_thread = execute_crew_in_thread()
            
            # Update the UI from the thread
            update_ui_with_result(message_from_thread)
        
        # Create and start the thread
        analysis_thread = threading.Thread(target=thread_target_wrapper)
        analysis_thread.start()
    
    # Create welcome text
    welcome_text = ft.Text(
        'Welcome to GPSE Strategy Runner!',
        size=20,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )
    
    # Create the run analysis button
    run_button = ft.ElevatedButton(
        text='Run GPSE Analysis',
        on_click=start_gpse_analysis,
        width=300
    )
    
    # Create the open output file button
    open_file_button = ft.ElevatedButton(
        text='Open Output File',
        on_click=open_generated_file,
        width=300,
        disabled=True  # Initially disabled
    )
    
    # Add controls to the page
    page.controls = [
        welcome_text,
        ft.Container(height=20),  # Add some spacing
        run_button,
        ft.Container(height=10),  # Add some spacing
        open_file_button,
        ft.Container(height=10),  # Add some spacing
        status_display
    ]
    
    # Update the page to show the controls
    page.update()


# Run the application
if __name__ == "__main__":
    ft.app(target=main)
