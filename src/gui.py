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
        
        # Make window not resizable for simplicity
        self.root.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="🧬 Gene Builder", font=('Helvetica', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle = ttk.Label(main_frame, text="Extract gene sequences from Ensembl", 
                            font=('Helvetica', 10))
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Gene symbol input
        ttk.Label(main_frame, text="Gene Symbol:", font=('Helvetica', 11, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        
        self.gene_entry = ttk.Entry(main_frame, width=30, font=('Helvetica', 11))
        self.gene_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.gene_entry.insert(0, "lrfn1")
        
        # Species selection
        ttk.Label(main_frame, text="Species:", font=('Helvetica', 11, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        
        self.species_var = tk.StringVar(value=config.DEFAULT_SPECIES)
        species_combo = ttk.Combobox(main_frame, textvariable=self.species_var, 
                                     width=28, state='readonly')
        species_combo['values'] = (
            'danio_rerio (Zebrafish)',
            'homo_sapiens (Human)',
            'mus_musculus (Mouse)',
            'rattus_norvegicus (Rat)'
        )
        species_combo.current(0)
        species_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Canonical only checkbox
        self.canonical_var = tk.BooleanVar(value=config.DEFAULT_CANONICAL_ONLY)
        canonical_check = ttk.Checkbutton(main_frame, 
                                         text="Only extract canonical transcript (recommended)",
                                         variable=self.canonical_var)
        canonical_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Extract button
        self.extract_btn = ttk.Button(main_frame, text="Extract Gene", 
                                      command=self.extract_gene,
                                      width=20)
        self.extract_btn.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        self.progress.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Output log
        ttk.Label(main_frame, text="Log:", font=('Helvetica', 11, 'bold')).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, width=65, height=15, 
                                                  font=('Monaco', 9), wrap=tk.WORD)
        self.log_text.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Buttons at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Open Output Folder", 
                  command=self.open_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
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
        self.progress.start()
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

