"""
================================================================================
PROGRESS INDICATOR POPUP - LOADING DISPLAY DURING ANALYSIS
================================================================================

PURPOSE:
    Provides a modal progress popup that displays real-time analysis progress
    with estimated time remaining. Used during long-running database scans
    (Dynamite mode) to keep users informed and indicate responsiveness.

FEATURES:
    - Modal window that blocks interaction with main window
    - Progress bar with percentage display
    - Estimated time remaining calculation
    - Non-blocking UI updates via update_idletasks()

USAGE EXAMPLE:
    popup = LoadingPopup(root, title="Scanning Database...", total_steps=1500)
    for i in range(1500):
        # ... perform work ...
        popup.update_progress(i)
    popup.close()
================================================================================
"""

import tkinter as tk
from tkinter import ttk
import time


class LoadingPopup:
    """
    Modal progress popup window for long-running analysis operations.
    
    Displays a progress bar, percentage completion, and estimated time remaining.
    Blocks interaction with parent window (grab_set) to prevent concurrent analysis.
    
    Attributes:
        win (tk.Toplevel): Modal popup window
        pb (ttk.Progressbar): Progress bar widget (0-100%)
        label (tk.Label): Status text showing percentage and ETA
        total (int): Total steps for progress calculation
        start_time (float): Unix timestamp of popup creation for ETA calculation
    """
    
    def __init__(self, master, title="Processing...", total_steps=100):
        """
        Create and display a progress popup window.
        
        Args:
            master (tk.Tk or tk.Frame): Parent window for popup
            title (str): Window title and label text (default: "Processing...")
            total_steps (int): Total number of steps in operation (default: 100)
                              Used to calculate percentage and ETA
        
        Notes:
            - Window is modal (grab_set) preventing parent interaction
            - Window is non-resizable and fixed at 400x120 pixels
            - Progress bar is initially at 0%
            - Start time is recorded for ETA calculation
        """
        self.win = tk.Toplevel(master)
        self.win.title(title)
        self.win.geometry("400x120")
        self.win.resizable(False, False)
        self.win.grab_set()  # Modal: blocks parent window interaction

        # Title label
        tk.Label(self.win, text=title, font=("Arial", 12, "bold")).pack(pady=10)

        # Progress bar (horizontal, 0-100%)
        self.pb = ttk.Progressbar(self.win, orient="horizontal",
                                  length=350, mode="determinate")
        self.pb.pack(pady=5)

        # Percentage and ETA label
        self.label = tk.Label(self.win, text="0%", font=("Arial", 10))
        self.label.pack()

        # Progress tracking
        self.total = total_steps
        self.start_time = time.time()

    def update_progress(self, current):
        """
        Update progress bar and estimated time remaining display.
        
        Args:
            current (int): Current step number (0 to total_steps)
        
        Workflow:
            1. Set progress bar value and maximum
            2. Calculate percentage completed
            3. Calculate elapsed time and average time per step
            4. Estimate remaining time: avg_time * (total - current)
            5. Update label with percentage and ETA
            6. Process pending GUI events (update_idletasks) to display changes
        
        Notes:
            - ETA is estimated and approximate
            - At step 0, assumes 0 seconds remaining (division by zero protection)
            - Uses update_idletasks() for non-blocking display refresh
            - No window blocking during update
        """
        # Update progress bar: set maximum and current value
        self.pb["maximum"] = self.total
        self.pb["value"] = current

        # Calculate percentage completed (0-100)
        pct = (current / self.total) * 100

        # Calculate estimated time remaining
        elapsed = time.time() - self.start_time
        avg = elapsed / current if current > 0 else 0  # Avoid division by zero
        remaining = avg * (self.total - current)

        # Update status label with percentage and ETA
        self.label.config(
            text=f"{pct:.1f}% — Estimated time remaining ~ {remaining:.1f} s"
        )

        # Process pending GUI events to display progress update
        self.win.update_idletasks()

    def close(self):
        """
        Close and destroy the progress popup window.
        
        Restores interaction with parent window by removing modal grab.
        Should be called when analysis operation completes.
        """
        self.win.destroy()

