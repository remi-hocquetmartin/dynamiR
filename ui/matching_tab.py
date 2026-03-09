"""
================================================================================
MATCHING TAB: Direct microRNA-to-mRNA Sequence Alignment
================================================================================

PURPOSE:
    Implements the "Matching" analysis mode where users provide both a microRNA
    sequence and an mRNA sequence to find binding sites within a specified seed
    region. This is the direct pairwise comparison approach.

FUNCTIONALITY:
    1. Input Collection:
       - microRNA: Database ID, file, or direct sequence entry
       - mRNA (target): GenBank ID, file, or direct sequence entry
       - Seed Range: Position range (e.g., 2-7) where pairing must be perfect
    
    2. Sequence Processing:
       - Reads sequences from files (FASTA format)
       - Handles T→U conversion (DNA to RNA)
       - Validates seed range format
    
    3. Analysis:
       - Calls backend matching algorithm
       - Generates visual alignment representations
       - Displays statistics (Watson-Crick pairs, wobble pairs)
    
    4. Result Display:
       - Shows alignment visualization in results pane
       - Multiple binding sites displayed sequentially
       - Statistics per binding site

ARCHITECTURE:
    MatchingTab (tk.Frame) manages:
    - Input panel (left): InputBlock widgets for each sequence type
    - Result display: Text widget receiving formatted alignment output
    - Event handling: "Parse" button triggers analysis workflow
================================================================================
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import re

# UI components
from ui.widgets import InputBlock

# Utility functions
from utils.parsers import parse_range_text
from utils.file_readers import read_sequence_from_file

# Backend algorithm
from backend.stub_backend import backend_match_micro_to_mrna


class MatchingTab(tk.Frame):
    """
    User interface for direct microRNA-to-mRNA binding site matching.
    
    Extends:
        tk.Frame: Tkinter frame container
    
    Attributes:
        result_text (tk.Text): Read-only text widget displaying analysis results
        micro_block (InputBlock): Input component for microRNA selection
        mrna_block (InputBlock): Input component for mRNA (target) selection
        seed_entry (tk.Entry): Input field for seed region range (e.g., "2-7")
    """

    def __init__(self, master, result_text_widget):
        """
        Initialize the Matching tab UI.
        
        Args:
            master (tk.Widget): Parent widget (tab container)
            result_text_widget (tk.Text): Shared text widget for result display
        
        Stores reference to result text widget for displaying analysis results
        and initializes current_result for download functionality.
        """
        super().__init__(master)
        self.result_text = result_text_widget
        self.current_result = ""  # Store result for download functionality
        self.master_tab = master   # Reference to parent tab for button placement
        
        # Bind resize events to reposition download button
        self.result_text.bind("<Configure>", self._on_result_resize)
        
        self.build_ui()

    def build_ui(self):
        """
        Construct the user interface layout.
        
        Layout:
            Left panel (width=250px, fixed):
            ├── microRNA InputBlock (radio buttons + entry/file selector)
            ├── mRNA InputBlock (radio buttons + entry/file selector)
            ├── Seed Range InputBlock (simplified, sequence-only)
            └── Parse Button
        
        Note:
            Seed block is simplified to hide radio buttons and show only
            the range entry field (typical format: "2-7").
        """
        # ==== LEFT PANEL (INPUT CONTROLS) ====
        left = tk.Frame(self, width=250)
        left.pack(side="left", fill="y", padx=8, pady=8)
        left.pack_propagate(False)  # Maintain fixed width

        # ---- microRNA Input Block ----
        # Allows selection of microRNA source: database ID, FASTA file, or direct sequence
        self.micro_block = InputBlock(
            left, 
            "microRNA:", 
            allow_filetypes=[("FASTA files", "*.fa *.fasta")], 
            dbid_tooltip="Enter a miRNA database ID (e.g., MIMAT0007560)",
            file_tooltip="FASTA format (.fa, .fasta)",
            seq_tooltip="Enter a microRNA sequence (e.g., AUGAA...)",
            dbid_placeholder="e.g., MIMAT0007560",
            seq_placeholder="e.g., AUGAA..."
        )
        self.micro_block.pack(fill="x", pady=8)

        # ---- mRNA Input Block ----
        # Allows selection of target mRNA: GenBank ID, file, or direct sequence
        self.mrna_block = InputBlock(
            left, 
            "mRNA:", 
            allow_filetypes=[("FASTA or GenBank", "*.fa *.fasta *.gb *.gbk")],
            dbid_tooltip="Enter an mRNA GenBank ID (e.g., NM_002111.8)",
            file_tooltip="FASTA or GenBank format (.fa, .fasta, .gb, .gbk)",
            seq_tooltip="Enter an mRNA sequence (e.g., AUGAA...)",
            dbid_placeholder="e.g., NM_002111.8",
            seq_placeholder="e.g., AUGAA..."
        )
        self.mrna_block.pack(fill="x", pady=8)
        # Override the "DB ID" label to "GenBank ID" for mRNA context
        self.mrna_block.rb_dbid.config(text="GenBank ID")

        # ---- Seed Range Input Block ----
        # Simplified version: only accepts position range (e.g., "2-7")
        # Radio buttons are hidden to reduce clutter
        self.seed_input = InputBlock(
            left,
            "Seed:",
            dbid_tooltip="Not used for Seed",
            file_tooltip="Not used for Seed",
            seq_tooltip="Nucleotide positions in microRNA that must match perfectly (e.g., positions 2-7)",
            seq_placeholder="e.g., 2-7"
        )
        
        # Hide the radio buttons and help icons (not needed for seed input)
        self.seed_input.rb_dbid.grid_remove()
        self.seed_input.rb_file.grid_remove()
        self.seed_input.rb_seq.grid_remove()
        self.seed_input.dbid_q.place_forget()
        self.seed_input.file_q.place_forget()
        self.seed_input.seq_q.place_forget()
        
        # Position help button after "Seed:" label using place() geometry manager
        label_widget = self.seed_input.winfo_children()[0]  # Reference the label
        self.seed_input.seq_q.place(in_=label_widget, relx=1.0, x=6, rely=0.5, anchor="w")
        
        # Hide file-related widgets (not applicable to seed input)
        self.seed_input.dbid_entry.grid_remove()
        self.seed_input.file_btn.grid_remove()
        self.seed_input.file_label.grid_remove()
        self.seed_input.clear_btn.grid_remove()
        
        # Show only the sequence entry field
        self.seed_input.seq_entry.grid(row=1, column=0, columnspan=3, sticky="w", padx=6, pady=3)
        self.seed_input.pack(fill="x", pady=8)
        
        # Create convenient reference to seed entry field
        self.seed_entry = self.seed_input.seq_entry

    # ========================================================================
    # DOWNLOAD BUTTON SETUP
    # ========================================================================

        """
        Create download button that will be positioned in results area corner.
        Initially hidden, positioned when results are available.
        Uses floppy disk emoji (💾) with flat style to match Dynamite mode.
        """
        self.download_btn = tk.Button(
            self.master_tab,
            text="💾",  # Save icon (floppy disk)
            font=("Arial", 12),
            relief="flat",
            cursor="hand2",
            command=self.save_result_to_file
        )
        # Button will be positioned in top-right via place() geometry manager

        # ---- Parse Button ----
        # Initiates the analysis workflow
        tk.Button(left, text="Parse", command=self.on_parse).pack(pady=(8, 0))

    def on_parse(self):
        """
        Parse user inputs and execute the matching analysis.
        
        Workflow:
            1. Collect inputs from all three input blocks
            2. Validate seed range format
            3. Retrieve sequences based on user's selection
                (database lookup, file read, or use inline sequence)
            4. Build metadata dictionary
            5. Call backend matching algorithm
            6. Display formatted results
        
        Error Handling:
            - Displays error dialogs for invalid seed format
            - Catches missing inputs with descriptive messages
            - Reports backend processing errors
        """

        # ==== STEP 1: COLLECT USER INPUTS ====
        micro_mode, micro_val = self.micro_block.get_value()
        mrna_mode, mrna_val = self.mrna_block.get_value()
        seed_text = self.seed_entry.get().strip()
        
        # Exclude placeholder text from validation
        if seed_text == "e.g., 2-7":
            seed_text = ""

        # ==== STEP 2: PARSE SEED RANGE ====
        # Convert string format "2-7" to tuple (2, 7)
        try:
            rng = parse_range_text(seed_text)
        except Exception as e:
            messagebox.showerror("Invalid Seed Range", str(e))
            return

        # ==== STEP 3: RETRIEVE SEQUENCES ====
        try:
            micro_seq, micro_meta = self.retrieve_seq(micro_mode, micro_val, "microRNA")
            mrna_seq, mrna_meta = self.retrieve_seq(mrna_mode, mrna_val, "mRNA")
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return

        # ==== STEP 4: BUILD METADATA CONTAINER ====
        # Structured metadata enables backend to track source of each sequence
        meta = {
            "micro": {
                "source": micro_mode,     # "dbid", "file", or "sequence"
                "data": micro_meta,       # {"dbid": ...} or {"file": ...} or {"inline": True}
            },
            "mrna": {
                "source": mrna_mode,      # "dbid", "file", or "sequence"
                "data": mrna_meta,        # {"dbid": ...} or {"file": ...} or {"inline": True}
            },
            "range": rng  # Tuple of (seed_start, seed_end)
        }

        # ==== STEP 5: CALL BACKEND ALGORITHM ====
        results = backend_match_micro_to_mrna(micro_seq, mrna_seq, rng, meta)

        # ==== STEP 6: DISPLAY RESULTS ====
        self.display_results(results)

    def retrieve_seq(self, mode, value, label):
        """
        Retrieve sequence and metadata based on input mode.
        
        Three input modes are supported:
        
        1. Database ID (dbid):
            - Returns empty sequence string (backend will fetch)
            - Metadata contains: {"dbid": <id>}
        
        2. File (file):
            - Reads sequence from FASTA or GenBank file
            - Returns parsed sequence and metadata
            - Metadata includes: {"file": <path>, "id": ..., "description": ...}
        
        3. Direct Sequence (sequence):
            - User typed sequence directly
            - Performs cleanup (remove whitespace, uppercase)
            - Converts T→U (DNA to RNA)
            - Metadata: {"inline": True}
        
        Args:
            mode (str): Input mode ("dbid", "file", or "sequence")
            value (str): Input value (ID string, file path, or sequence)
            label (str): Human-readable label for error messages
        
        Returns:
            tuple: (sequence_string, metadata_dict)
        
        Raises:
            ValueError: If input is missing or invalid
        """
        if mode == "dbid":
            # Database lookup mode
            if not value:
                raise ValueError(f"No {label} database ID provided.")
            return ("", {"dbid": value})
        
        elif mode == "file":
            # File input mode
            if not value:
                raise ValueError(f"No {label} file selected.")
            seq, meta = read_sequence_from_file(value)
            # Include original filepath in metadata for backend reference
            return (seq, {"file": value, **meta})
        
        elif mode == "sequence":
            # Direct sequence input mode
            if not value:
                raise ValueError(f"No {label} sequence entered.")
            # Normalize: remove whitespace and convert to uppercase
            seq = re.sub(r"\s+", "", value).upper()
            # Perform T→U conversion (DNA to RNA)
            seq = seq.replace("T", "U")
            return (seq, {"inline": True})
        
        raise ValueError("Invalid input mode.")

    def display_results(self, result):
        """
        Display analysis results in the shared result text widget.
        
        The result text widget is normally in disabled state (read-only).
        This function temporarily enables it, inserts results, and re-disables it.
        Also positions the download button in the top-right corner.
        
        Args:
            result (str): Formatted result string from backend algorithm
        """
        self.result_text.config(state="normal")       # Enable editing
        self.result_text.delete("1.0", tk.END)        # Clear existing content
        self.result_text.insert(tk.END, result)       # Insert results
        self.result_text.config(state="disabled")     # Re-disable editing
        
        # Store result for download functionality
        self.current_result = result
        
        # Position download button in top-right corner
        self.after(50, self._place_download_button)

    def _on_result_resize(self, event):
        """
        Reposition download button when result text widget is resized.
        
        This ensures the button stays in the top-right corner even when
        the window is resized.
        
        Args:
            event (tk.Event): Tkinter event containing widget dimensions
        """
        # Only reposition if button is visible (has results)
        if self.download_btn.winfo_ismapped():
            self._place_download_button()

    def _place_download_button(self):
        """
        Position the download button in the top-right corner of the results area.
        
        Uses place() geometry manager with relative positioning (relx=1.0) to ensure
        the button stays fixed to the right edge even when the window is resized.
        """
        # Get reference to result text widget's parent (the right panel)
        result_parent = self.result_text.master
        
        # Check if parent is ready
        if not result_parent.winfo_ismapped():
            return
        
        result_parent.update_idletasks()
        
        # Positioning constants
        margin_right = 5    # Right margin from edge
        margin_top = 5      # Top margin
        
        # Position with relx=1.0 to stay anchored to right edge during resize
        self.download_btn.place(
            in_=result_parent,
            relx=1.0,           # Stick to right edge (1.0 = 100%)
            x=-margin_right,    # Offset from right edge
            y=margin_top,       # Top margin
            anchor="ne"         # Northeast anchor (top-right corner)
        )

    def save_result_to_file(self):
        """
        Export analysis results to a text file.
        
        Opens file save dialog, writes current results to selected file.
        
        Workflow:
            1. Open file save dialog (default: .txt format)
            2. User selects save location and filename
            3. Write results text to file
            4. Show confirmation message
        
        Error Handling:
            - Catches user cancel (dialog closed without selection)
            - Reports file write errors
        """
        if not self.current_result:
            messagebox.showwarning("No Results", "No results to download. Run analysis first.")
            return
        
        try:
            # Open file save dialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="matching_results.txt"
            )
            
            # User cancelled dialog
            if not filepath:
                return
            
            # Write results to file
            with open(filepath, 'w') as f:
                f.write(self.current_result)
            
            messagebox.showinfo("Success", f"Results saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results:\n{str(e)}")


