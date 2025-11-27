#!/usr/bin/env python3
"""
Gene Builder GUI
================

Simple graphical interface for extracting gene sequences from Ensembl.
No command line needed!

"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
import os

# Add parent directory to path for config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our config and main script
import config
from src.gene_to_genbank import process_gene

class GeneBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_SIZE[0]}x{config.WINDOW_SIZE[1]}")
        
        # Allow resizing
        self.root.resizable(True, True)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container to hold everything with padding
        container = ttk.Frame(self.root, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns to expand
        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)  # Log area expands
        
        # Title Area
        title_frame = ttk.Frame(container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        title = ttk.Label(title_frame, text="🧬 Gene Builder", font=('Helvetica', 24, 'bold'))
        title.pack()
        
        subtitle = ttk.Label(title_frame, text="Extract gene sequences from Ensembl", 
                            font=('Helvetica', 12))
        subtitle.pack(pady=(5, 0))
        
        # Input Area
        input_frame = ttk.Frame(container)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # Gene Symbol
        ttk.Label(input_frame, text="Gene Symbol:", font=('Helvetica', 13, 'bold')).grid(
            row=0, column=0, sticky="w", pady=10)
        
        self.gene_entry = ttk.Entry(input_frame, font=('Helvetica', 13))
        self.gene_entry.grid(row=0, column=1, sticky="ew", padx=(15, 0), pady=10)
        self.gene_entry.insert(0, "lrfn1")
        
        # Species
        ttk.Label(input_frame, text="Species:", font=('Helvetica', 13, 'bold')).grid(
            row=1, column=0, sticky="w", pady=10)
        
        self.species_var = tk.StringVar(value=config.DEFAULT_SPECIES)
        species_combo = ttk.Combobox(input_frame, textvariable=self.species_var, 
                                     font=('Helvetica', 13), state='readonly')
        species_combo['values'] = (
            'danio_rerio (Zebrafish)',
            'homo_sapiens (Human)',
            'mus_musculus (Mouse)',
            'rattus_norvegicus (Rat)'
        )
        species_combo.current(0)
        species_combo.grid(row=1, column=1, sticky="ew", padx=(15, 0), pady=10)
        
        # Checkbox
        self.canonical_var = tk.BooleanVar(value=config.DEFAULT_CANONICAL_ONLY)
        canonical_check = ttk.Checkbutton(container, 
                                         text="Only extract canonical transcript (recommended)",
                                         variable=self.canonical_var)
        # Note: Checkbutton font styling is platform dependent, often ignored
        canonical_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Extract Button
        self.extract_btn = ttk.Button(container, text="Extract Gene", 
                                      command=self.extract_gene)
        self.extract_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20), ipady=5)
        
        # Log Area (Expands)
        log_frame = ttk.LabelFrame(container, text="Process Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=60, height=10, 
                                                  font=('Monaco', 11), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Progress bar
        self.progress = ttk.Progressbar(container, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15, 5))
        
        # Bottom Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Open Output Folder", 
                  command=self.open_output).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=10)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        
    def extract_gene(self):
        """Extract gene in background thread"""
        gene = self.gene_entry.get().strip()
        
        if not gene:
            messagebox.showwarning("Input Required", "Please enter a gene symbol")
            return
        
        # Start progress bar
        self.progress.start(10) # Speed up animation
        self.extract_btn.config(state='disabled')
        self.clear_log()
        
        # Run in background thread
        thread = threading.Thread(target=self._extract_thread, args=(gene,))
        thread.daemon = True
        thread.start()
        
    def _extract_thread(self, gene):
        """Background thread for extraction"""
        try:
            # Get species code (remove display name)
            species_full = self.species_var.get()
            species = species_full.split(' ')[0]
            
            canonical_only = self.canonical_var.get()
            
            self.log(f"🔍 Extracting gene: {gene}")
            self.log(f"📊 Species: {species}")
            self.log(f"🎯 Canonical only: {canonical_only}")
            self.log("-" * 60)
            
            # Redirect stdout to capture print statements
            import io
            from contextlib import redirect_stdout
            
            log_capture = io.StringIO()
            
            with redirect_stdout(log_capture):
                files = process_gene(
                    gene, 
                    species=species,
                    output_dir=config.OUTPUT_DIR,
                    canonical_only=canonical_only
                )
            
            # Show captured log
            for line in log_capture.getvalue().split('\n'):
                if line.strip():
                    self.log(line)
            
            self.log("-" * 60)
            self.log(f"✅ Success! Generated {len(files)} file(s):")
            for f in files:
                self.log(f"   📄 {os.path.basename(f)}")
            self.log("")
            self.log(f"💾 Files saved to: {os.path.abspath(config.OUTPUT_DIR)}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success!",
                f"Generated {len(files)} GenBank file(s)\n\n"
                f"Files are in the '{config.OUTPUT_DIR}' folder.\n"
                f"You can open them in ApE or SnapGene."
            ))
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to extract gene:\n\n{str(e)}\n\n"
                "Check the log for details."
            ))
        finally:
            # Stop progress bar and re-enable button
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.extract_btn.config(state='normal'))
    
    def open_output(self):
        """Open output folder in Finder"""
        import subprocess
        output_path = os.path.abspath(config.OUTPUT_DIR)
        if os.path.exists(output_path):
            subprocess.call(['open', output_path])
        else:
            messagebox.showinfo("Info", "Output folder is empty. Extract a gene first!")

def main():
    root = tk.Tk()
    app = GeneBuilderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
