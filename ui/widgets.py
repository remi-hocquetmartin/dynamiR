"""
================================================================================
REUSABLE UI COMPONENTS AND WIDGETS
================================================================================

PURPOSE:
    Provides reusable Tkinter widget components for consistent UI design
    across the application. Implements tooltip system, input blocks, and
    database selection interface.

COMPONENTS:
    1. Tooltip: Hover-over help text with configurable delay
    2. InputBlock: Unified input component with three input modes
       - Database ID entry
       - File selection
       - Direct sequence entry
       All with integrated help tooltips and placeholder text

DESIGN PHILOSOPHY:
    - Minimal styling (flat relief, no unnecessary decorations)
    - Reusable components for consistency
    - Placeholder text for field guidance
    - Contextual help via tooltips
    - Flexible configuration for different input types
================================================================================
"""

import tkinter as tk
from tkinter import filedialog
import os


class Tooltip:
    """
    Hover-over tooltip widget for Tkinter.
    
    Creates a small popup window that appears when user hovers over a widget,
    providing contextual help text. Automatically hides when cursor leaves.
    
    Attributes:
        widget (tk.Widget): Widget to attach tooltip to
        text (str): Tooltip text to display
        delay (int): Milliseconds before tooltip appears (default: 250)
        tw (tk.Toplevel): Toplevel window containing tooltip (None when hidden)
    """

    def __init__(self, widget, text, delay=250):
        """
        Initialize tooltip.
        
        Args:
            widget (tk.Widget): Widget to attach tooltip to
            text (str): Tooltip text
            delay (int): Delay in milliseconds before showing (default: 250)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id = None  # ID for scheduled show event
        self.tw = None         # Toplevel window
        
        # Bind mouse events to show/hide tooltip
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<Motion>", self._on_motion, add="+")

    @staticmethod
    def attach(widget, text, delay=250):
        """
        Convenience method to attach tooltip to widget.
        
        Args:
            widget (tk.Widget): Widget to attach tooltip to
            text (str): Tooltip text
            delay (int): Delay in milliseconds before showing
        
        Returns:
            Tooltip: The Tooltip instance (stored on widget to prevent garbage collection)
        """
        widget._tooltip = Tooltip(widget, text, delay)
        return widget._tooltip

    def _on_enter(self, event=None):
        """Handle mouse entering widget - schedule tooltip display."""
        self._schedule()

    def _on_leave(self, event=None):
        """Handle mouse leaving widget - cancel tooltip and hide."""
        self._unschedule()
        self._hide()

    def _on_motion(self, event):
        """Handle mouse motion - move tooltip with cursor."""
        if self.tw:
            x = event.x_root + 12  # 12px offset from cursor
            y = event.y_root + 8
            self.tw.wm_geometry(f"+{x}+{y}")

    def _schedule(self):
        """Schedule tooltip display after delay."""
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        """Cancel scheduled tooltip display."""
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        """Display tooltip window."""
        if self.tw or not self.text:
            return
        
        # Position tooltip near cursor
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        
        # Create toplevel window (borderless popup)
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create label with tooltip text
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#2c3e50",           # Dark gray background
            foreground="#ecf0f1",           # Light text
            relief="flat",
            borderwidth=0,
            font=("Helvetica", 9),
            padx=8,
            pady=5
        )
        label.pack(ipadx=6, ipady=3)
        self.tw = tw

    def _hide(self):
        """Hide tooltip window."""
        if self.tw:
            try:
                self.tw.destroy()
            except Exception:
                pass
            self.tw = None


class InputBlock(tk.Frame):
    """
    Reusable input block component with three input modes.
    
    Provides unified interface for collecting sequence data from:
    1. Database ID (e.g., MIMAT0007560)
    2. File (FASTA or GenBank format)
    3. Direct sequence entry
    
    Each mode has its own entry widget and all include integrated tooltips.
    
    Attributes:
        choice_var (tk.StringVar): Tracks which input mode is selected
        rb_dbid, rb_file, rb_seq (tk.Radiobutton): Mode selection buttons
        dbid_entry (tk.Entry): Database ID entry field
        file_btn (tk.Button): File selection button
        file_label (tk.Label): Displays selected filename
        seq_entry (tk.Entry): Direct sequence entry field
        selected_path (str): Path to selected file
    """

    def __init__(self, master, label_text, allow_filetypes=None, 
                 file_tooltip=None, dbid_tooltip=None, seq_tooltip=None, 
                 dbid_placeholder=None, seq_placeholder=None, **kwargs):
        """
        Initialize input block.
        
        Args:
            master (tk.Widget): Parent widget
            label_text (str): Label to display (e.g., "microRNA:")
            allow_filetypes (list): File types for dialog (default: all files)
            file_tooltip (str): Help text for file mode
            dbid_tooltip (str): Help text for database ID mode
            seq_tooltip (str): Help text for sequence mode
            dbid_placeholder (str): Placeholder text for ID entry
            seq_placeholder (str): Placeholder text for sequence entry
            **kwargs: Additional arguments for tk.Frame
        """
        super().__init__(master, **kwargs)
        self.allow_filetypes = allow_filetypes or [("All files", "*.*")]

        # ==== LABEL ====
        tk.Label(
            self, 
            text=label_text, 
            bg="#fafafa"
        ).grid(row=0, column=0, sticky="w", pady=(6, 4), padx=6)

        # ==== INPUT MODE SELECTOR ====
        self.choice_var = tk.StringVar(value="dbid")  # Default: database ID

        # Radio button styling
        radio_font = ("Helvetica", 11)

        # Option 1: Database ID
        self.rb_dbid = tk.Radiobutton(
            self, 
            text="DB ID", 
            variable=self.choice_var, 
            value="dbid",
            font=radio_font,
            highlightthickness=0
        )
        self.rb_dbid.grid(row=1, column=0, sticky="w", padx=6, pady=2)
        
        # Option 2: File
        self.rb_file = tk.Radiobutton(
            self, 
            text="File", 
            variable=self.choice_var, 
            value="file",
            font=radio_font,
            highlightthickness=0
        )
        self.rb_file.grid(row=2, column=0, sticky="w", padx=6, pady=2)
        
        # Option 3: Direct Sequence
        self.rb_seq = tk.Radiobutton(
            self, 
            text="Sequence", 
            variable=self.choice_var, 
            value="sequence",
            font=radio_font,
            highlightthickness=0
        )
        self.rb_seq.grid(row=3, column=0, sticky="w", padx=6, pady=2)

        # ==== HELP TOOLTIPS ====
        # Help icon for database ID mode
        self.dbid_q = tk.Label(self, text="?", fg="#5b7b99", cursor="hand2", 
                               font=("Helvetica", 9, "bold"))
        self.dbid_q.place(in_=self.rb_dbid, relx=1.0, x=6, rely=0.5, anchor="w")
        dbid_tooltip_text = dbid_tooltip if dbid_tooltip else "Enter a database ID"
        Tooltip.attach(self.dbid_q, dbid_tooltip_text)

        # Help icon for file mode
        self.file_q = tk.Label(self, text="?", fg="#5b7b99", cursor="hand2", 
                               font=("Helvetica", 9, "bold"))
        self.file_q.place(in_=self.rb_file, relx=1.0, x=6, rely=0.5, anchor="w")
        file_tooltip_text = file_tooltip if file_tooltip else "Select a file"
        Tooltip.attach(self.file_q, file_tooltip_text)

        # Help icon for sequence mode
        self.seq_q = tk.Label(self, text="?", fg="#5b7b99", cursor="hand2", 
                              font=("Helvetica", 9, "bold"))
        self.seq_q.place(in_=self.rb_seq, relx=1.0, x=1, rely=0.5, anchor="w")
        seq_tooltip_text = seq_tooltip if seq_tooltip else "Enter a sequence"
        Tooltip.attach(self.seq_q, seq_tooltip_text)

        # ==== DATABASE ID ENTRY ====
        self.dbid_placeholder = dbid_placeholder if dbid_placeholder else "e.g., MIMAT0007560"
        self.dbid_entry = tk.Entry(self, width=40, fg="gray")
        self.dbid_entry.insert(0, self.dbid_placeholder)
        self.dbid_entry.grid(row=1, column=1, sticky="w", padx=(6, 0), pady=3)
        self.dbid_entry.bind("<FocusIn>", self._on_dbid_focus_in)
        self.dbid_entry.bind("<FocusOut>", self._on_dbid_focus_out)

        # ==== FILE SELECTOR ====
        self.file_btn = tk.Button(
            self, 
            text="Select file", 
            command=self.select_file
        )
        self.file_btn.grid(row=2, column=1, sticky="w", padx=(6, 0), pady=3)

        # File name display
        self.file_label = tk.Label(
            self, 
            text="No file selected", 
            anchor="w"
        )
        self.file_label.grid(row=2, column=2, sticky="w", padx=4, pady=3)

        # Clear file button
        self.clear_btn = tk.Button(
            self, 
            text="✕", 
            command=self.clear_file
        )
        self.clear_btn.grid(row=2, column=3, sticky="w", pady=3)
        self.clear_btn.grid_remove()  # Hidden until file selected

        # ==== SEQUENCE ENTRY ====
        self.seq_placeholder = seq_placeholder if seq_placeholder else "e.g., AUGAA..."
        self.seq_entry = tk.Entry(self, width=40, fg="gray")
        self.seq_entry.insert(0, self.seq_placeholder)
        self.seq_entry.grid(row=3, column=1, columnspan=2, sticky="w", padx=(6, 0), pady=3)
        self.seq_entry.bind("<FocusIn>", self._on_seq_focus_in)
        self.seq_entry.bind("<FocusOut>", self._on_seq_focus_out)

        # Store selected file path
        self.selected_path = None

    # ========================================================================
    # PLACEHOLDER TEXT MANAGEMENT
    # ========================================================================

    def _on_dbid_focus_in(self, event):
        """Clear placeholder when database ID entry receives focus."""
        if self.dbid_entry.get() == self.dbid_placeholder:
            self.dbid_entry.delete(0, tk.END)
            self.dbid_entry.config(fg="black")

    def _on_dbid_focus_out(self, event):
        """Show placeholder if database ID entry is empty."""
        if self.dbid_entry.get() == "":
            self.dbid_entry.insert(0, self.dbid_placeholder)
            self.dbid_entry.config(fg="#999999")

    def _on_seq_focus_in(self, event):
        """Clear placeholder when sequence entry receives focus."""
        if self.seq_entry.get() == self.seq_placeholder:
            self.seq_entry.delete(0, tk.END)
            self.seq_entry.config(fg="black")

    def _on_seq_focus_out(self, event):
        """Show placeholder if sequence entry is empty."""
        if self.seq_entry.get() == "":
            self.seq_entry.insert(0, self.seq_placeholder)
            self.seq_entry.config(fg="#999999")

    # ========================================================================
    # FILE MANAGEMENT
    # ========================================================================

    def select_file(self):
        """
        Open file selection dialog and store selected path.
        
        Updates UI with selected filename and shows clear button.
        """
        path = filedialog.askopenfilename(filetypes=self.allow_filetypes)
        if path:
            self.selected_path = path
            # Display filename in label
            self.file_label.config(text=os.path.basename(path))
            # Update button text with filename
            try:
                self.file_btn.config(text=os.path.basename(path))
            except Exception:
                pass
            self.clear_btn.grid()  # Show clear button
        else:
            self.file_label.config(text="No file selected")
            # Restore button text
            try:
                self.file_btn.config(text="Select file")
            except Exception:
                pass
            self.clear_btn.grid_remove()

    def clear_file(self):
        """
        Clear selected file and reset UI.
        
        Removes the file path and restores button appearance.
        """
        self.selected_path = None
        self.file_label.config(text="No file selected")
        try:
            self.file_btn.config(text="Select file")
        except Exception:
            pass
        self.clear_btn.grid_remove()

    # ========================================================================
    # VALUE RETRIEVAL
    # ========================================================================

    def get_value(self):
        """
        Get current input value and mode.
        
        Returns tuple based on selected input mode:
        - ("dbid", <id_string>): Database ID mode
        - ("file", <file_path>): File mode
        - ("sequence", <sequence>): Direct sequence mode
        
        Placeholder text is excluded from returned values.
        
        Returns:
            tuple: (mode, value) where mode is one of "dbid", "file", "sequence"
        """
        mode = self.choice_var.get()
        
        if mode == "dbid":
            dbid_val = self.dbid_entry.get().strip()
            # Exclude placeholder from return value
            if dbid_val == self.dbid_placeholder:
                dbid_val = ""
            return ("dbid", dbid_val)
        
        elif mode == "file":
            return ("file", self.selected_path)
        
        elif mode == "sequence":
            seq_val = self.seq_entry.get().strip()
            # Exclude placeholder from return value
            if seq_val == self.seq_placeholder:
                seq_val = ""
            return ("sequence", seq_val)
        
        return (None, None)


class SeedBlock(tk.Frame):
    """
    Specialized input block for seed region specification.
    
    Simplified version that only accepts position range input (e.g., "2-7").
    Consistent visual styling with InputBlock for UI coherence.
    
    Attributes:
        entry (tk.Entry): Input field for position range
        placeholder (str): Default placeholder text
    """

    def __init__(self, master, placeholder="e.g., 2-7", tooltip_text=None, **kwargs):
        """
        Initialize seed block.
        
        Args:
            master (tk.Widget): Parent widget
            placeholder (str): Placeholder text for input
            tooltip_text (str): Help text tooltip
            **kwargs: Additional arguments for tk.Frame
        """
        super().__init__(master, **kwargs)
        
        self.placeholder = placeholder
        
        # ==== LABEL ====
        tk.Label(
            self, 
            text="Seed:"
        ).grid(row=0, column=0, sticky="w", pady=(6, 4), padx=6)
        
        # ==== HELP BUTTON ====
        help_btn = tk.Label(self, text="?", cursor="hand2", font=("Arial", 10, "bold"))
        help_btn.grid(row=0, column=1, sticky="w", padx=(0, 6))
        tooltip_msg = tooltip_text if tooltip_text else "Position range\n(e.g., 2-7)"
        Tooltip.attach(help_btn, tooltip_msg)
        
        # ==== ENTRY FIELD ====
        self.entry = tk.Entry(self, width=40, fg="gray")
        self.entry.insert(0, self.placeholder)
        self.entry.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=3)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Clear placeholder when entry receives focus."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="black")
    
    def _on_focus_out(self, event):
        """Show placeholder if entry is empty."""
        if self.entry.get() == "":
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="gray")
    
    def get_value(self):
        """
        Get seed range value, excluding placeholder.
        
        Returns:
            str: Position range (e.g., "2-7") or empty string if placeholder
        """
        val = self.entry.get().strip()
        if val == self.placeholder:
            return ""
        return val


