"""
================================================================================
DynamiR - MAIN APPLICATION WINDOW
================================================================================

MODULE PURPOSE:
    This module is the core GUI layer that initializes and manages the main
    application window. It creates the tabbed interface that users interact with
    to perform microRNA binding site analysis on target mRNA sequences.

APPLICATION OVERVIEW:
    The microRNA Binding Site Analysis Tool provides two complementary analysis
    modes through a unified graphical interface:
    
    1. MATCHING MODE (Direct Analysis)
       - User provides: microRNA sequence + target mRNA sequence + seed region
       - Analysis: Finds all binding sites where microRNA seed matches mRNA
       - Use case: Verify specific microRNA-mRNA interactions
       - Speed: Immediate (direct alignment)
    
    2. DYNAMITE MODE (Database Scanning)
       - User provides: Target mRNA sequence + seed region
       - Analysis: Screens entire database (~1,500 microRNAs) to find all binders
       - Use case: Discover which microRNAs can bind to target mRNA
       - Speed: ~5-10 seconds per scan (threaded, non-blocking)

MODULE STRUCTURE:
    - MicroApp class: Main application window (extends tk.Tk)
    - __init__(): Window initialization, layout, styling, tab creation
    - Color scheme: Professional minimal palette (#fafafa bg, #333333 text)
    - ttk styling: Consistent appearance across all widgets
    - Tab integration: MatchingTab and DynamiteTab from ui/ package

DEPENDENCIES:
    - tkinter (tk, ttk): GUI framework
    - ui.matching_tab.MatchingTab: Direct analysis interface
    - ui.dynamite_tab.DynamiteTab: Database scanning interface
    - sys, os: Module path management for relative imports

EXECUTION FLOW:
    When launched (either directly or via projet.py):
    1. MicroApp.__init__() creates and configures window
    2. Applies unified ttk styling theme
    3. Creates tabbed notebook container
    4. Instantiates Matching tab with result display area
    5. Instantiates Dynamite tab with result display area
    6. Enters mainloop() - waits for user interaction
    7. User can switch tabs, enter inputs, run analyses
    8. Analyses display results in side-panel text widgets
================================================================================
"""

import sys
import os
"""
PATH SETUP:
    Add current script directory to Python's module search path.
    This enables relative imports from ui/ and utils/ packages regardless
    of where the script is executed from.
"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk

"""
UI MODULE IMPORTS:
    MatchingTab: Handles direct microRNA-to-mRNA alignment interface
    DynamiteTab: Handles database scanning interface
"""
from ui.matching_tab import MatchingTab
from ui.dynamite_tab import DynamiteTab


class MicroApp(tk.Tk):
    """
    Main Application Window - Tkinter Root Widget
    
    Extends:
        tk.Tk: Tkinter root window class
    
    Purpose:
        Manages the complete GUI environment including window layout, tabbed
        interface, color scheme, and integration of analysis mode tabs.
    
    Attributes:
        (All GUI state delegated to child widgets - no instance attributes stored)
    
    Child Components:
        - ttk.Notebook: Tabbed container for different analysis modes
        - MatchingTab: Direct microRNA-mRNA analysis interface
        - DynamiteTab: Database scanning interface
        - Text widgets: Result display areas for each tab
    """

    def __init__(self):
        """
        Initialize the main application window with complete GUI setup.
        
        This method performs comprehensive window configuration including
        sizing, layout, color scheme, styling, and tab creation.
        
        INITIALIZATION WORKFLOW:
        
        Step 1: TKINTER WINDOW SETUP
            - Call parent tk.Tk.__init__()
            - Set window title
            - Set initial size (1000x650 pixels)
            - Set minimum size (850x550 pixels)
            - Configure background color
        
        Step 2: COLOR SCHEME DEFINITION
            - bg_color (#fafafa): Light gray background (professional, minimal)
            - text_color (#333333): Dark gray text (high contrast, readable)
            - accent_color (#5b7b99): Muted blue accents (selected tabs, highlights)
        
        Step 3: TTK STYLE CONFIGURATION
            - Use 'clam' theme as base (clean, modern appearance)
            - Style ttk.Notebook tabs (selected/unselected appearance)
            - Style ttk.Frame backgrounds
            - Apply consistent fonts and padding
        
        Step 4: TAB 1 - MATCHING MODE (Direct Analysis)
            Layout:
                ┌─────────────────────────────────────┐
                │  Matching Tab                       │
                ├──────────────┬──────────────────────┤
                │   Inputs     │    Results Display   │
                │   (left)     │    (right, Text)     │
                │              │                      │
                │  - microRNA  │  (disabled, updated  │
                │  - mRNA      │   by analysis)       │
                │  - Seed      │                      │
                │  - Parse btn │                      │
                └──────────────┴──────────────────────┘
            
            Components:
                - match_right: Text widget for result display (read-only)
                - MatchingTab: Input panel and analysis logic
                - Both packed in match_frame
        
        Step 5: TAB 2 - DYNAMITE MODE (Database Scanning)
            Layout:
                ┌─────────────────────────────────────┐
                │  Dynamite Tab                       │
                ├──────────────┬──────────────────────┤
                │   Inputs     │    Results Display   │
                │   (left)     │    (right, Text)     │
                │              │  + Download Button   │
                │  - mRNA      │  (appears after run) │
                │  - Seed      │                      │
                │  - Scan btn  │                      │
                └──────────────┴──────────────────────┘
            
            Components:
                - dynamite_right: Text widget for result display (read-only)
                - DynamiteTab: Input panel, threading, progress tracking
                - Both packed in dynamite_frame
        
        CONFIGURATION DETAILS:
            
            Font Selection:
                - UI labels: Helvetica (system standard)
                - Results text: Monaco (monospace, alignment clarity)
            
            Text Widget Configuration:
                - Font: Monaco 9pt (readable monospace for sequence alignment)
                - Background: White (#ffffff) for result clarity
                - Foreground: Dark text color for contrast
                - State: Disabled initially (no user editing)
                - Relief: Solid (minimal 3D effect)
            
            Packing Strategy:
                - Tabs: fill="both", expand=True (maximize use of space)
                - Frames: side="left"/"right" with fill="y" (side-by-side layout)
                - Text widgets: side="right", fill="both", expand=True (take remaining space)
        """
        super().__init__()
        
        # ============================================================================
        # STEP 1: TKINTER WINDOW CONFIGURATION
        # ============================================================================
        
        self.title("DynamiR")
        self.geometry("1000x650")
        self.minsize(850, 550)
        
        # ============================================================================
        # STEP 2: COLOR SCHEME DEFINITION (Professional Minimal Palette)
        # ============================================================================
        
        bg_color = "#fafafa"        # Light gray background (professional, minimal)
        text_color = "#333333"      # Dark text (high contrast, readable)
        accent_color = "#5b7b99"    # Muted blue accents (selected tabs, highlights)
        
        self.configure(bg=bg_color)
        
        # ============================================================================
        # STEP 3: TTK STYLE CONFIGURATION (Consistent Widget Appearance)
        # ============================================================================
        
        """
        Apply consistent styling to all ttk widgets using Style API.
        Base theme: 'clam' provides clean, modern appearance without excessive 3D effects.
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk.Notebook (tabbed container)
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 10), padding=[12, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", accent_color), ("!selected", "#e8e8e8")],
                  foreground=[("selected", "white"), ("!selected", text_color)])
        
        # Configure ttk.Frame
        style.configure("TFrame", background=bg_color)
        
        # ============================================================================
        # STEP 4 & 5: CREATE TABBED INTERFACE WITH BOTH ANALYSIS MODES
        # ============================================================================
        
        """
        Create main notebook (tabbed container) that fills entire window.
        Will contain two tabs: Matching and Dynamite.
        """
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # ============================================================================
        # TAB 1: MATCHING MODE - DIRECT MICRORNA-TO-MRNA ANALYSIS
        # ============================================================================
        
        """
        Layout: [Inputs (left)] | [Results (right)]
        
        Purpose: User provides microRNA and mRNA sequences, specifies seed region.
                 Analysis finds all binding sites where seed matches target.
        """
        
        # Container frame for this tab
        match_frame = ttk.Frame(notebook)
        
        # Results display area (right side)
        match_right = tk.Text(
            match_frame, 
            width=60, 
            font=("Monaco", 9),         # Monospace font for sequence alignment
            bg="#ffffff",               # White background for result clarity
            fg=text_color,
            relief="solid", 
            borderwidth=0
        )
        match_right.pack(side="right", fill="both", expand=True, padx=1, pady=1)
        match_right.config(state="disabled")  # Read-only: analysis updates content
        
        # Input panel (left side) - instantiate MatchingTab UI
        match_tab = MatchingTab(match_frame, match_right)
        match_tab.pack(side="left", fill="y", padx=0, pady=0)
        
        # Add this tab to notebook with label
        notebook.add(match_frame, text="Matching")

        # ============================================================================
        # TAB 2: DYNAMITE MODE - HIGH-THROUGHPUT DATABASE SCANNING
        # ============================================================================
        
        """
        Layout: [Inputs (left)] | [Results (right) + Download Button]
        
        Purpose: User provides mRNA sequence, specifies seed region.
                 Analysis screens entire microRNA database (~1,500 sequences).
                 Results show all microRNAs that can bind with scores.
                 Download button allows export of results to file.
        """
        
        # Container frame for this tab
        dynamite_frame = ttk.Frame(notebook)
        
        # Results display area (right side)
        dynamite_right = tk.Text(
            dynamite_frame, 
            width=60, 
            font=("Monaco", 9),         # Monospace font for sequence alignment
            bg="#ffffff",               # White background for result clarity
            fg=text_color,
            relief="solid", 
            borderwidth=0
        )
        dynamite_right.pack(side="right", fill="both", expand=True, padx=1, pady=1)
        dynamite_right.config(state="disabled")  # Read-only: analysis updates content
        
        # Input panel (left side) - instantiate DynamiteTab UI
        dynamite_tab = DynamiteTab(dynamite_frame, dynamite_right)
        dynamite_tab.pack(side="left", fill="y", padx=0, pady=0)
        
        # Add this tab to notebook with label
        notebook.add(dynamite_frame, text="Dynamite")


# ================================================================================
# APPLICATION ENTRY POINT - Direct Execution
# ================================================================================

if __name__ == "__main__":
    """
    Script Entry Point - Direct Launch
    
    This code only executes when gui_frontend.py is run directly:
        python3 gui_frontend.py
    
    It does NOT execute when gui_frontend.py is imported as a module
    (e.g., from projet.py).
    
    Workflow:
        1. Create MicroApp instance (initializes complete GUI)
        2. Call mainloop() to enter event loop
        3. Event loop runs indefinitely, processing user interactions
        4. Mainloop exits when user closes window
        5. Program terminates
    
    Notes:
        - The primary recommended entry point is projet.py (not this file directly)
        - However, this file can be executed independently for testing/development
        - Both entry points (projet.py and gui_frontend.py) create the same GUI
    """
    app = MicroApp()
    app.mainloop()
