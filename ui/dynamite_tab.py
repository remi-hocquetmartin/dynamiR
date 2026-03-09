"""
================================================================================
DYNAMITE TAB: High-Throughput Database Scanning
================================================================================

PURPOSE:
    Implements the "Dynamite" analysis mode for scanning an entire microRNA
    database against a user-provided mRNA sequence to identify all potential
    binding microRNAs within a specified seed region.

FUNCTIONALITY:
    1. Input Collection:
       - mRNA (target): GenBank ID, file, or direct sequence
       - Seed Range: Position range where perfect pairing is required
    
    2. Processing:
       - Loads entire miRNA database (~1,500+ mature microRNAs)
       - Iteratively tests each microRNA against target mRNA
       - Reports progress via callback mechanism
       - Displays loading popup during long-running analysis
    
    3. Analysis Results:
       - Ranked list of binding microRNAs
       - Scoring includes: Watson-Crick pairs, wobble (G-U) pairs
       - Binding percentage calculation
       - Supplementary pairing positions outside seed region
    
    4. Output:
       - Formatted results table
       - Download functionality to save results as .txt file
       - Result display in read-only text widget

ARCHITECTURE:
    DynamiteTab (tk.Frame) manages:
    - Input panel (left): InputBlock widget for mRNA
    - Threading: Background worker thread for long-running analysis
    - Progress tracking: LoadingPopup for user feedback
    - Download button: Dynamically positioned in results area
    - Result display: Text widget receiving formatted results table
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import re
import threading

# UI components
from ui.widgets import InputBlock
from ui.loading_popup import LoadingPopup

# Utility functions
from utils.parsers import parse_range_text
from utils.file_readers import read_sequence_from_file

# Backend algorithm
from backend.stub_backend import backend_dynamite_on_mrna


class DynamiteTab(tk.Frame):
    """
    User interface for high-throughput microRNA database scanning.
    
    Extends:
        tk.Frame: Tkinter frame container
    
    Attributes:
        result_text (tk.Text): Read-only text widget displaying analysis results
        result_container (tk.Widget): Parent container for result_text
        mrna_block (InputBlock): Input component for mRNA selection
        seed_entry (tk.Entry): Input field for seed region range
        download_btn (tk.Button): Button to save results to file
        popup (LoadingPopup): Progress indication during analysis
    """

    def __init__(self, master, result_text_widget):
        """
        Initialize the Dynamite tab UI.
        
        Args:
            master (tk.Widget): Parent widget
            result_text_widget (tk.Text): Shared text widget for result display
        """
        super().__init__(master)
        self.result_text = result_text_widget
        self.result_container = result_text_widget.master

        # Loading popup (hidden until analysis starts)
        self.popup = None

        # ==== DOWNLOAD BUTTON (Initially Hidden) ====
        # Positioned dynamically in the result area top-right corner
        self.download_btn = tk.Button(
            self.result_container,
            text="💾",  # Save icon
            font=("Arial", 12),
            relief="flat",
            cursor="hand2",
            command=self.save_result_to_file
        )
        self.download_btn.place_forget()  # Hide initially
        
        # Bind container resize event to reposition download button
        self.result_container.bind("<Configure>", self._on_container_resize)

        self.build_ui()

    # ========================================================================
    # UI CONSTRUCTION (LEFT INPUT PANEL)
    # ========================================================================

    def build_ui(self):
        """
        Construct the user interface layout.
        
        Layout:
            Left panel (width=250px, fixed):
            ├── mRNA InputBlock (radio buttons + entry/file selector)
            ├── Seed Range InputBlock (simplified, sequence-only)
            └── Parse Button
        """
        # ==== LEFT PANEL (INPUT CONTROLS) ====
        left = tk.Frame(self, width=250)
        left.pack(side="left", fill="y", padx=8, pady=8)
        left.pack_propagate(False)  # Maintain fixed width

        # ---- mRNA Input Block ----
        # Allows selection of target mRNA: GenBank ID, file, or direct sequence
        self.mrna_block = InputBlock(
            left,
            "mRNA:",
            allow_filetypes=[("Sequence files", "*.fa *.fasta *.gb *.gbk")],
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

        # ---- Parse Button ----
        # Initiates the analysis workflow (launches background thread)
        tk.Button(left, text="Parse", command=self.on_parse).pack(pady=(8, 0))

    # ========================================================================
    # USER INPUT PARSING & WORKFLOW INITIATION
    # ========================================================================

    def on_parse(self):
        """
        Parse user inputs and initiate background analysis.
        
        Workflow:
            1. Collect inputs from input blocks
            2. Validate seed range format
            3. Retrieve target mRNA sequence
            4. Create loading popup
            5. Launch background worker thread
        
        The background thread calls backend_dynamite_on_mrna() and
        reports progress via callback.
        
        Error Handling:
            - Displays error dialogs for invalid inputs
            - Catches missing seed range or mRNA specification
        """
        # ==== COLLECT INPUTS ====
        mrna_mode, mrna_val = self.mrna_block.get_value()
        seed_text = self.seed_entry.get().strip()
        
        # Exclude placeholder text from validation
        if seed_text == "e.g., 2-7":
            seed_text = ""

        # ==== PARSE SEED RANGE ====
        # Convert string format "2-7" to tuple (2, 7)
        try:
            rng = parse_range_text(seed_text)
        except Exception as e:
            messagebox.showerror("Invalid Seed Range", str(e))
            return

        # ==== RETRIEVE mRNA SEQUENCE ====
        try:
            mrna_seq, mrna_meta = self.retrieve_seq(mrna_mode, mrna_val)
        except Exception as e:
            messagebox.showerror("mRNA Error", str(e))
            return

        # ==== BUILD METADATA CONTAINER ====
        # Structured metadata enables backend to track mRNA source
        meta = {
            "mrna": {
                "source": mrna_mode,      # "dbid", "file", or "sequence"
                "data": mrna_meta,        # {"dbid": ...} or {"file": ...} or {"inline": True}
            },
            "range": rng  # Tuple of (seed_start, seed_end)
        }

        # ==== SHOW LOADING POPUP ====
        # Provides user feedback during long-running database scan
        self.popup = LoadingPopup(self, title="Scanning miRNA Database", total_steps=100)

        # ==== LAUNCH BACKGROUND WORKER THREAD ====
        # Prevents UI freezing during analysis
        threading.Thread(
            target=self._background_run,
            args=(mrna_seq, rng, meta),
            daemon=True
        ).start()

    # ========================================================================
    # BACKGROUND WORKER EXECUTION
    # ========================================================================

    def _background_run(self, mrna_seq, rng, meta):
        """
        Execute the database scanning algorithm in background thread.
        
        This runs in a separate thread to prevent UI freezing during
        the potentially long-running analysis (scanning ~1,500+ microRNAs).
        
        Args:
            mrna_seq (str): Target mRNA sequence
            rng (tuple): Seed range (start, end)
            meta (dict): Metadata dictionary with mRNA source info
        
        The result is passed to _on_done() via thread-safe after() callback.
        """
        try:
            # Call backend algorithm with progress callback
            result = backend_dynamite_on_mrna(
                mrna_seq,
                rng,
                meta,
                progress_callback=self._on_progress
            )
        except Exception as e:
            # Capture any errors for display
            result = f"ERROR_WORKER: {e}"

        # Queue result for main thread via thread-safe callback
        self.after(0, lambda: self._on_done(result))

    # ========================================================================
    # PROGRESS TRACKING
    # ========================================================================

    def _on_progress(self, current, total):
        """
        Callback triggered by backend algorithm to report progress.
        
        Args:
            current (int): Number of microRNAs processed so far
            total (int): Total number of microRNAs in database
        
        This is called from background thread, so we use after() to
        safely update UI from main thread.
        """
        self.after(0, lambda: self._update_popup_progress(current, total))

    def _update_popup_progress(self, current, total):
        """
        Update loading popup progress bar.
        
        Args:
            current (int): Current progress value
            total (int): Maximum progress value
        """
        if not self.popup:
            return

        self.popup.total = total
        try:
            self.popup.update_progress(current)
        except AttributeError:
            # Fallback for alternative popup interface
            if hasattr(self.popup, "update"):
                self.popup.update(current, total)

    # ========================================================================
    # RESULT HANDLING
    # ========================================================================

    def _on_done(self, result):
        """
        Handle completion of background analysis.
        
        Args:
            result (str): Formatted results table or error message
        
        Workflow:
            1. Close loading popup
            2. Check for errors
            3. Display results
            4. Show download button
        """

        # ==== CLOSE LOADING POPUP ====
        if self.popup:
            try:
                self.popup.close()
            except:
                pass
            self.popup = None

        # ==== CHECK FOR ERRORS ====
        if isinstance(result, str) and result.startswith("ERROR_WORKER"):
            messagebox.showerror("Worker Error", result)
            self.display_results("An error occurred:\n" + result)
            return

        # ==== DISPLAY RESULTS ====
        self.display_results(result)

        # ==== SHOW DOWNLOAD BUTTON ====
        self.after(50, self._place_download_button)

    # ========================================================================
    # DOWNLOAD BUTTON POSITIONING
    # ========================================================================

    def _on_container_resize(self, event):
        """
        Reposition download button when result container is resized.
        
        Args:
            event (tk.Event): Tkinter event containing widget dimensions
        """
        if self.download_btn.winfo_ismapped():
            self._place_download_button()

    def _place_download_button(self):
        """
        Position the download button in the top-right corner of the results area.
        
        Uses place() geometry manager with relative positioning (relx=1.0) to ensure
        the button stays fixed to the right edge even when the window is resized.
        """
        container = self.result_container

        # Check if container is ready
        if not container.winfo_ismapped():
            return

        container.update_idletasks()
        
        # Positioning constants
        margin_right = 5    # Right margin from edge
        margin_top = 5      # Top margin
        
        # Position with relx=1.0 to stay anchored to right edge during resize
        self.download_btn.place(
            relx=1.0,           # Stick to right edge (1.0 = 100%)
            x=-margin_right,    # Offset from right edge
            y=margin_top,       # Top margin
            anchor="ne"         # Northeast anchor (top-right corner)
        )

    # ========================================================================
    # SEQUENCE RETRIEVAL
    # ========================================================================

    def retrieve_seq(self, mode, value):
        """
        Retrieve target mRNA sequence and metadata based on input mode.
        
        Three input modes are supported:
        
        1. Database ID (dbid):
            - Returns empty sequence string (backend will fetch from GenBank)
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
        
        Returns:
            tuple: (sequence_string, metadata_dict)
        
        Raises:
            ValueError: If input is missing or invalid
        """
        if mode == "dbid":
            # Database lookup mode
            if not value:
                raise ValueError("No GenBank ID provided.")
            return ("", {"dbid": value})

        elif mode == "file":
            # File input mode
            if not value:
                raise ValueError("No file selected.")
            seq, meta = read_sequence_from_file(value)
            # Include original filepath in metadata for backend reference
            return (seq, {"file": value, **meta})

        elif mode == "sequence":
            # Direct sequence input mode
            if not value:
                raise ValueError("No sequence entered.")
            # Normalize: remove whitespace and convert to uppercase
            seq = re.sub(r"\s+", "", value).upper()
            # Perform T→U conversion (DNA to RNA)
            seq = seq.replace("T", "U")
            return (seq, {"inline": True})

        raise ValueError("Invalid input mode.")

    # ========================================================================
    # RESULT DISPLAY
    # ========================================================================

    def display_results(self, results):
        """
        Display analysis results in the shared result text widget.
        
        The result text widget is normally in disabled state (read-only).
        This function temporarily enables it, inserts results, and re-disables it.
        
        Args:
            results (str): Formatted results table from backend algorithm
        """

        # Convert dict to string if needed (for compatibility)
        if isinstance(results, dict):
            results_text = "\n".join(f"--- {k} ---\n{v}" for k, v in results.items())
        else:
            results_text = str(results)

        # Display results in read-only text widget
        self.result_text.config(state="normal")        # Enable editing
        self.result_text.delete("1.0", "end")          # Clear existing content
        self.result_text.insert("end", results_text)   # Insert results
        self.result_text.config(state="disabled")      # Re-disable editing

    # ========================================================================
    # FILE DOWNLOAD
    # ========================================================================

    def save_result_to_file(self):
        """
        Save current results to a text file.
        
        Workflow:
            1. Extract results text from read-only widget
            2. Show file save dialog
            3. Write results to selected file
            4. Confirm to user
        """
        # Extract results content
        content = self.result_text.get("1.0", "end").strip()
        
        if not content:
            messagebox.showinfo("Empty", "There is no result to save.")
            return

        # Show file save dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
        )

        if not filepath:
            return

        # Write to file
        try:
            with open(filepath, "w") as f:
                f.write(content)
            messagebox.showinfo("Success", "Results saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")

