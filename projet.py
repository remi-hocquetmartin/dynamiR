"""
================================================================================
DynamiR - PROJECT ENTRY POINT
================================================================================

PURPOSE:
    This is the main entry point for launching DynamiR, the microRNA Binding Site
    Analysis Tool. Execute this script to start the complete application with
    the graphical user interface.

FUNCTIONALITY:
    - Initializes the application environment
    - Imports and instantiates the main application window
    - Starts the Tkinter event loop for the GUI
    - Handles graceful application startup and shutdown

USAGE:
    Command line: python3 projet.py
    
    The application will launch with a graphical interface containing:
    - "Matching" tab: Direct microRNA-to-mRNA alignment analysis
    - "Dynamite" tab: Database scanning of all microRNAs against target mRNA

ARCHITECTURE:
    This launcher script performs minimal initialization and delegates all
    UI/logic to gui_frontend.py, which manages the main application window
    and tab interfaces.

EXIT CODES:
    0: Successful execution (user closed application normally)
    1: Unexpected error during startup or execution
================================================================================
"""

import sys
import os
import traceback


def main():
    """
    Main application entry point.
    
    Initializes the GUI environment and launches the Tkinter event loop.
    Handles any errors during startup and provides user feedback.
    
    Workflow:
        1. Add script directory to Python path for relative imports
        2. Import the main GUI application class
        3. Create application instance
        4. Start main event loop
        5. Handle errors gracefully
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Ensure relative imports work from script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Import the main application class
        from gui_frontend import MicroApp
        
        # Create and launch the application
        app = MicroApp()
        
        # Start the main event loop (blocks until application closes)
        app.mainloop()
        
        # Execution completed successfully
        return 0
        
    except ImportError as e:
        """
        Handle import errors (missing modules or files).
        """
        print(f"ERROR: Failed to import required modules: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1
        
    except Exception as e:
        """
        Handle unexpected errors during startup or execution.
        """
        print(f"ERROR: Unexpected error during application startup: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    """
    Script entry point: only execute main() when run directly (not imported).
    This is standard Python practice for executable scripts and modules.
    """
    exit_code = main()
    sys.exit(exit_code)
