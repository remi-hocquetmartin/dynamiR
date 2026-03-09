import tkinter as tk
from tkinter import messagebox, filedialog
import re
import threading

from ui.widgets import InputBlock
from utils.parsers import parse_range_text
from utils.file_readers import read_sequence_from_file
from ui.loading_popup import LoadingPopup

from backend.stub_backend import backend_blast_on_mrna


class BlastTab(tk.Frame):
    """UI for Blast mode."""
    def __init__(self, master, result_text_widget):
        super().__init__(master)

        # Widget d'affichage de résultat (Text)
        self.result_text = result_text_widget
        self.result_container = result_text_widget.master

        # Popup de chargement
        self.popup = None

        # Bouton téléchargement (invisible au départ)
        self.download_btn = tk.Button(
            self.result_container,
            text="💾",
            font=("Arial", 12),
            relief="flat",
            cursor="hand2",
            command=self.save_result_to_file
        )
        self.download_btn.place_forget()
        
        # Bind window resize to reposition button
        self.result_container.bind("<Configure>", self._on_container_resize)

        self.build_ui()


    # ------------------------------------------------------------------
    # UI PANEL (gauche)
    # ------------------------------------------------------------------
    def build_ui(self):
        left = tk.Frame(self, width=250)
        left.pack(side="left", fill="y", padx=8, pady=8)
        left.pack_propagate(False)

        # mRNA input block
        self.mrna_block = InputBlock(
            left,
            "mRNA:",
            allow_filetypes=[("Sequence files", "*.fa *.fasta *.gb *.gbk")],
            dbid_tooltip="Enter a mRNA GenBank ID\n(e.g., NM_002111.8)",
            file_tooltip="FASTA or GenBank format\n(.fa, .fasta, .gb, .gbk)",
            seq_tooltip="Enter an mRNA sequence\n(e.g., ATGAA...)",
            dbid_placeholder="e.g., NM_002111.8",
            seq_placeholder="e.g., ATGAA..."
        )
        self.mrna_block.pack(fill="x", pady=8)
        # Replace "DB id" with "GenBank ID" for mRNA
        self.mrna_block.rb_dbid.config(text="GenBank ID")

        # Create a simplified InputBlock for Seed that only uses sequence mode
        self.seed_input = InputBlock(
            left,
            "Seed:",
            dbid_tooltip="Not used for Seed",
            file_tooltip="Not used for Seed",
            seq_tooltip="Position range of miRNA sequence\nthat must match perfectly\n(e.g., positions 2-7)",
            seq_placeholder="e.g., 2-7"
        )
        # Hide the radio buttons by removing them from view
        self.seed_input.rb_dbid.grid_remove()
        self.seed_input.rb_file.grid_remove()
        self.seed_input.rb_seq.grid_remove()
        self.seed_input.dbid_q.place_forget()
        self.seed_input.file_q.place_forget()
        self.seed_input.seq_q.place_forget()
        # Place seq_q right after "Seed:" label using place() like the other help buttons
        # Position it relative to the label
        label_widget = self.seed_input.winfo_children()[0]  # Get the label
        self.seed_input.seq_q.place(in_=label_widget, relx=1.0, x=6, rely=0.5, anchor="w")
        # Hide file-related widgets
        self.seed_input.dbid_entry.grid_remove()
        self.seed_input.file_btn.grid_remove()
        self.seed_input.file_label.grid_remove()
        self.seed_input.clear_btn.grid_remove()
        # Show only the sequence entry (move to row 1)
        self.seed_input.seq_entry.grid(row=1, column=0, columnspan=3, sticky="w", padx=6, pady=3)
        self.seed_input.pack(fill="x", pady=8)
        
        # For backward compatibility, keep seed_entry pointing to the actual entry
        self.seed_entry = self.seed_input.seq_entry

        tk.Button(left, text="Parse", command=self.on_parse).pack(pady=(8, 0))


    # ------------------------------------------------------------------
    # Lancement du worker
    # ------------------------------------------------------------------
    def on_parse(self):
        mrna_mode, mrna_val = self.mrna_block.get_value()
        seed_text = self.seed_entry.get().strip()
        
        # Exclude placeholder from being treated as actual input
        if seed_text == "e.g., 2-7":
            seed_text = ""

        # Parse seed
        try:
            rng = parse_range_text(seed_text)
        except Exception as e:
            messagebox.showerror("Invalid seed", str(e))
            return

        # Retrieve sequence
        try:
            mrna_seq, mrna_meta = self.retrieve_seq(mrna_mode, mrna_val)
        except Exception as e:
            messagebox.showerror("mRNA error", str(e))
            return

        meta = {
            "mrna_source": mrna_mode,
            "mrna_meta": mrna_meta,
            "range": rng
        }

        # Popup
        self.popup = LoadingPopup(self, title="Processing miRNA matching", total_steps=100)

        # Worker thread
        threading.Thread(
            target=self._background_run,
            args=(mrna_seq, rng, meta),
            daemon=True
        ).start()


    # ------------------------------------------------------------------
    # Worker execution
    # ------------------------------------------------------------------
    def _background_run(self, mrna_seq, rng, meta):
        try:
            result = backend_blast_on_mrna(
                mrna_seq,
                rng,
                meta,
                progress_callback=self._on_progress
            )
        except Exception as e:
            result = f"ERROR_WORKER: {e}"

        self.after(0, lambda: self._on_done(result))


    # ------------------------------------------------------------------
    # Progress callback
    # ------------------------------------------------------------------
    def _on_progress(self, current, total):
        self.after(0, lambda: self._update_popup_progress(current, total))

    def _update_popup_progress(self, current, total):
        if not self.popup:
            return

        self.popup.total = total
        try:
            self.popup.update_progress(current)
        except AttributeError:
            if hasattr(self.popup, "update"):
                self.popup.update(current, total)


    # ------------------------------------------------------------------
    # After worker finishes
    # ------------------------------------------------------------------
    def _on_done(self, result):

        # Close popup
        if self.popup:
            try:
                self.popup.close()
            except:
                pass
            self.popup = None

        # Error?
        if isinstance(result, str) and result.startswith("ERROR_WORKER"):
            messagebox.showerror("Worker error", result)
            self.display_results("An error occurred:\n" + result)
            return

        # Display results
        self.display_results(result)

        # Place download button
        self.after(50, self._place_download_button)


    # ------------------------------------------------------------------
    # Place download button (always stick to right)
    # ------------------------------------------------------------------
    def _on_container_resize(self, event):
        """Reposition download button on container resize."""
        if self.download_btn.winfo_ismapped():
            self._place_download_button()

    def _place_download_button(self):
        container = self.result_container

        if not container.winfo_ismapped():
            return

        container.update_idletasks()
        w = container.winfo_width()

        margin = 36
        btn_width = 24

        x = w - (btn_width + margin)
        y = 5

        self.download_btn.place(x=x, y=y)


    # ------------------------------------------------------------------
    # Retrieve sequence
    # ------------------------------------------------------------------
    def retrieve_seq(self, mode, value):
        if mode == "dbid":
            if not value:
                raise ValueError("No DB id given.")
            return ("", {"dbid": value})

        elif mode == "file":
            if not value:
                raise ValueError("No file selected.")
            seq, meta = read_sequence_from_file(value)
            # Inclure le chemin du fichier pour le backend (comme Matching)
            return (seq, {"file": value, **meta})

        elif mode == "sequence":
            if not value:
                raise ValueError("No sequence entered.")
            seq = re.sub(r"\s+", "", value).upper()
            return (seq, {"inline": True})

        raise ValueError("Invalid mode.")


    # ------------------------------------------------------------------
    # Display results (with match count)
    # ------------------------------------------------------------------
    def display_results(self, results):
        """Insert results + compute match count."""

        # Convert dict to string if needed
        if isinstance(results, dict):
            results_text = "\n".join(f"--- {k} ---\n{v}" for k, v in results.items())
        else:
            results_text = str(results)

        # Count matches = count non-empty lines that look like data lines
        data_lines = [
            l for l in results_text.split("\n")
            if l.strip() != ""
            and not l.startswith("=")
            and not l.startswith("-")
            and not l.startswith("Range")
            and not l.startswith("Seed")
        ]
        match_count = len(data_lines)

        final_text =  results_text

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", final_text)
        self.result_text.config(state="disabled")


    # ------------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------------
    def save_result_to_file(self):
        content = self.result_text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Empty", "There is no result to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
        )

        if not filepath:
            return

        with open(filepath, "w") as f:
            f.write(content)

        messagebox.showinfo("Saved", "Results successfully saved.")
