# gui_app.py - Improved Compression GUI Application
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar, IntVar
import os
import threading
import time
import zipfile
import gzip
import bz2
from PIL import Image, ImageTk
import shutil
from pathlib import Path
import webbrowser

class CompressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Compressor")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Style configuration
        self.setup_styles()
        
        # Variables
        self.selected_file = StringVar()
        self.compression_method = StringVar(value="zip")
        self.quality_var = IntVar(value=85)
        self.progress_var = IntVar(value=0)
        self.compression_thread = None
        self.stop_compression = False
        self.compressed_files = []
        self.dark_mode = False
        
        # Initialize GUI
        self.setup_gui()
        self.center_window()
        self.create_menu()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TEntry', font=('Arial', 10), padding=5)
        self.style.configure('TCombobox', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Success.TLabel', foreground='green')
        self.style.configure('Error.TLabel', foreground='red')
        self.style.map('TButton', 
                      foreground=[('pressed', 'white'), ('active', 'blue')],
                      background=[('pressed', '!disabled', 'dark blue'), ('active', 'lightblue')])

    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.EW)
        
        self.logo = self.create_placeholder_logo()
        ttk.Label(header_frame, image=self.logo).grid(row=0, column=0, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=1, sticky=tk.W)
        ttk.Label(title_frame, text="Advanced File Compressor", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        ttk.Label(title_frame, text="Compress files with multiple algorithms").grid(row=1, column=0, sticky=tk.W)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding=(10, 5))
        file_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file, width=50)
        self.file_entry.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Compression settings
        settings_frame = ttk.LabelFrame(main_frame, text="Compression Settings", padding=(10, 5))
        settings_frame.grid(row=2, column=0, sticky=tk.EW, pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="Method:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.method_combo = ttk.Combobox(settings_frame, textvariable=self.compression_method,
                                       values=['zip', 'gzip', 'bzip2', 'image_lossy', 'all'], 
                                       state='readonly', width=15)
        self.method_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        self.method_combo.bind('<<ComboboxSelected>>', self.on_method_change)
        
        # Quality settings (for image compression)
        self.quality_frame = ttk.Frame(settings_frame)
        self.quality_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=(5, 0))
        
        ttk.Label(self.quality_frame, text="JPEG Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.quality_scale = ttk.Scale(self.quality_frame, from_=10, to=100, 
                                     variable=self.quality_var, orient=tk.HORIZONTAL)
        self.quality_scale.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        self.quality_value = ttk.Label(self.quality_frame, text="85%")
        self.quality_value.grid(row=0, column=2, padx=(0, 5))
        self.quality_scale.configure(command=self.update_quality_label)
        self.quality_frame.grid_remove()
        
        # Progress area
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=(10, 5))
        progress_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=500)
        self.progress_bar.grid(row=0, column=0, sticky=tk.EW)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to compress")
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, sticky=tk.EW, pady=(0, 10))
        
        self.compress_btn = ttk.Button(btn_frame, text="Start Compression", 
                                     command=self.start_compression)
        self.compress_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", 
                                  command=self.stop_compression_process, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        self.clear_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Compression Results", padding=(10, 5))
        results_frame.grid(row=5, column=0, sticky=tk.NSEW)
        main_frame.rowconfigure(5, weight=1)
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10, 
                                  font=('Consolas', 10), padx=5, pady=5)
        self.results_text.grid(row=0, column=0, sticky=tk.NSEW)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Configure text tags
        self.results_text.tag_configure('header', font=('Arial', 11, 'bold'))
        self.results_text.tag_configure('success', foreground='green')
        self.results_text.tag_configure('error', foreground='red')
        self.results_text.tag_configure('info', foreground='blue')
        self.results_text.tag_configure('warning', foreground='orange')
        
        # Bottom buttons
        bottom_btn_frame = ttk.Frame(main_frame)
        bottom_btn_frame.grid(row=6, column=0, sticky=tk.EW, pady=(5, 0))
        
        self.open_btn = ttk.Button(bottom_btn_frame, text="Open Output Folder", 
                                  command=self.open_output_folder, state='disabled')
        self.open_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.help_btn = ttk.Button(bottom_btn_frame, text="Help", 
                                  command=self.show_help)
        self.help_btn.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(bottom_btn_frame, text="Exit", command=self.root.quit).grid(row=0, column=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Clear All", command=self.clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_placeholder_logo(self):
        # In a real app, you would load an actual image here
        from PIL import Image, ImageTk
        try:
            img = Image.new('RGB', (48, 48), color='lightblue')
            return ImageTk.PhotoImage(img)
        except:
            return None

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = '#2d2d2d' if self.dark_mode else '#f0f0f0'
        fg = 'white' if self.dark_mode else 'black'
        
        self.root.configure(bg=bg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg)
        self.style.configure('TButton', background=bg)
        self.style.configure('TLabelframe', background=bg, foreground=fg)
        self.style.configure('TLabelframe.Label', background=bg, foreground=fg)
        
        self.results_text.configure(bg='#3d3d3d' if self.dark_mode else 'white',
                                  fg='white' if self.dark_mode else 'black',
                                  insertbackground='white' if self.dark_mode else 'black')

    def browse_file(self):
        filetypes = [
            ('All files', '*.*'),
            ('Text files', '*.txt'),
            ('Image files', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('Archive files', '*.zip *.rar *.7z'),
            ('Documents', '*.pdf *.doc *.docx *.xls *.xlsx')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select file to compress",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_file.set(filename)
            self.add_result(f"Selected file: {os.path.basename(filename)}", 'info')

    def on_method_change(self, event=None):
        method = self.compression_method.get()
        if method in ('image_lossy', 'all'):
            self.quality_frame.grid()
        else:
            self.quality_frame.grid_remove()

    def update_quality_label(self, val):
        self.quality_value.config(text=f"{int(float(val))}%")

    def clear_all(self):
        self.selected_file.set("")
        self.compression_method.set("zip")
        self.quality_var.set(85)
        self.progress_var.set(0)
        self.results_text.delete(1.0, tk.END)
        self.status_label.config(text="Ready to compress")
        self.quality_frame.grid_remove()
        self.compressed_files = []
        self.open_btn.config(state='disabled')
        self.add_result("Cleared all inputs and results", 'info')

    def add_result(self, text, tag=None):
        self.results_text.insert(tk.END, text + "\n", tag)
        self.results_text.see(tk.END)
        self.root.update_idletasks()

    def start_compression(self):
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select a file first!")
            return
            
        if not os.path.exists(self.selected_file.get()):
            messagebox.showerror("Error", "File not found!")
            return
            
        self.stop_compression = False
        self.compress_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.open_btn.config(state='disabled')
        
        self.compression_thread = threading.Thread(target=self.compress_file)
        self.compression_thread.daemon = True
        self.compression_thread.start()

    def stop_compression_process(self):
        self.stop_compression = True
        self.status_label.config(text="Stopping compression...")
        self.add_result("Compression stopped by user", 'warning')

    def compress_file(self):
        try:
            file_path = self.selected_file.get()
            method = self.compression_method.get()
            quality = self.quality_var.get()
            
            self.progress_var.set(0)
            self.status_label.config(text="Starting compression...")
            self.compressed_files = []

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            original_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)

            self.add_result("=== COMPRESSION STARTED ===", 'header')
            self.add_result(f"File: {filename}")
            self.add_result(f"Original size: {self.format_size(original_size)}")
            self.add_result(f"Method: {method.upper()}")
            self.add_result("")

            if self.stop_compression:
                return

            methods_to_run = []
            if method == 'all':
                methods_to_run = ['zip', 'gzip', 'bzip2']
                if self.is_image_file(file_path):
                    methods_to_run.append('image_lossy')
            else:
                methods_to_run = [method]

            total_methods = len(methods_to_run)
            for i, current_method in enumerate(methods_to_run):
                if self.stop_compression:
                    break
                    
                base_progress = (i / total_methods) * 100
                
                if current_method == 'zip':
                    self.compress_zip(file_path, name, original_size, base_progress)
                elif current_method == 'gzip':
                    self.compress_gzip(file_path, name, original_size, base_progress)
                elif current_method == 'bzip2':
                    self.compress_bzip2(file_path, name, original_size, base_progress)
                elif current_method == 'image_lossy':
                    if self.is_image_file(file_path):
                        self.compress_image_lossy(file_path, name, original_size, quality, base_progress)
                    else:
                        self.add_result("File is not an image, skipping lossy compression", 'warning')

            if not self.stop_compression:
                self.progress_var.set(100)
                self.status_label.config(text="Compression completed!")
                self.add_result("=== COMPRESSION COMPLETED ===", 'header')
                
                if self.compressed_files:
                    self.open_btn.config(state='normal')
                    self.add_result(f"✓ {len(self.compressed_files)} files compressed successfully", 'success')

        except Exception as e:
            self.add_result(f"✗ Error: {str(e)}", 'error')
            self.status_label.config(text="Compression error!")
        finally:
            self.compress_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

    def is_image_file(self, file_path):
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return os.path.splitext(file_path)[1].lower() in image_exts

    def compress_zip(self, file_path, name, original_size, base_progress=0):
        try:
            self.status_label.config(text="Compressing with ZIP...")
            self.progress_var.set(int(base_progress + 10))
            
            output_path = os.path.join(os.path.dirname(file_path), f"{name}_compressed.zip")
            start_time = time.time()
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
                
            compressed_size = os.path.getsize(output_path)
            ratio = self.calculate_ratio(original_size, compressed_size)
            
            self.compressed_files.append(output_path)
            
            self.add_result("--- ZIP Compression ---", 'header')
            self.add_result(f"✓ Output: {os.path.basename(output_path)}", 'success')
            self.add_result(f"✓ Size: {self.format_size(compressed_size)}", 'success')
            self.add_result(f"✓ Ratio: {ratio}", 'success')
            self.add_result(f"✓ Time: {time.time() - start_time:.2f}s", 'success')
            self.add_result("")
            
        except Exception as e:
            self.add_result(f"✗ ZIP Error: {str(e)}", 'error')

    def compress_gzip(self, file_path, name, original_size, base_progress=0):
        try:
            self.status_label.config(text="Compressing with GZIP...")
            self.progress_var.set(int(base_progress + 10))
            
            output_path = os.path.join(os.path.dirname(file_path), f"{name}_compressed.gz")
            start_time = time.time()
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            compressed_size = os.path.getsize(output_path)
            ratio = self.calculate_ratio(original_size, compressed_size)
            
            self.compressed_files.append(output_path)
            
            self.add_result("--- GZIP Compression ---", 'header')
            self.add_result(f"✓ Output: {os.path.basename(output_path)}", 'success')
            self.add_result(f"✓ Size: {self.format_size(compressed_size)}", 'success')
            self.add_result(f"✓ Ratio: {ratio}", 'success')
            self.add_result(f"✓ Time: {time.time() - start_time:.2f}s", 'success')
            self.add_result("")
            
        except Exception as e:
            self.add_result(f"✗ GZIP Error: {str(e)}", 'error')

    def compress_bzip2(self, file_path, name, original_size, base_progress=0):
        try:
            self.status_label.config(text="Compressing with BZIP2...")
            self.progress_var.set(int(base_progress + 10))
            
            output_path = os.path.join(os.path.dirname(file_path), f"{name}_compressed.bz2")
            start_time = time.time()
            
            with open(file_path, 'rb') as f_in:
                with bz2.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            compressed_size = os.path.getsize(output_path)
            ratio = self.calculate_ratio(original_size, compressed_size)
            
            self.compressed_files.append(output_path)
            
            self.add_result("--- BZIP2 Compression ---", 'header')
            self.add_result(f"✓ Output: {os.path.basename(output_path)}", 'success')
            self.add_result(f"✓ Size: {self.format_size(compressed_size)}", 'success')
            self.add_result(f"✓ Ratio: {ratio}", 'success')
            self.add_result(f"✓ Time: {time.time() - start_time:.2f}s", 'success')
            self.add_result("")
            
        except Exception as e:
            self.add_result(f"✗ BZIP2 Error: {str(e)}", 'error')

    def compress_image_lossy(self, file_path, name, original_size, quality, base_progress=0):
        try:
            self.status_label.config(text="Compressing image (lossy)...")
            self.progress_var.set(int(base_progress + 10))
            
            output_path = os.path.join(os.path.dirname(file_path), f"{name}_compressed_q{quality}.jpg")
            start_time = time.time()
            
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
            compressed_size = os.path.getsize(output_path)
            ratio = self.calculate_ratio(original_size, compressed_size)
            
            self.compressed_files.append(output_path)
            
            self.add_result("--- Image Compression ---", 'header')
            self.add_result(f"✓ Output: {os.path.basename(output_path)}", 'success')
            self.add_result(f"✓ Quality: {quality}%", 'success')
            self.add_result(f"✓ Size: {self.format_size(compressed_size)}", 'success')
            self.add_result(f"✓ Ratio: {ratio}", 'success')
            self.add_result(f"✓ Time: {time.time() - start_time:.2f}s", 'success')
            self.add_result("")
            
        except Exception as e:
            self.add_result(f"✗ Image Error: {str(e)}", 'error')

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def calculate_ratio(self, original, compressed):
        if original == 0:
            return "0.00%"
        ratio = (1 - (compressed / original)) * 100
        return f"{ratio:.2f}%"

    def open_output_folder(self):
        if not self.compressed_files:
            messagebox.showwarning("Warning", "No compressed files available!")
            return
            
        output_dir = os.path.dirname(self.compressed_files[0])
        if os.path.exists(output_dir):
            webbrowser.open(output_dir)
        else:
            messagebox.showerror("Error", "Output directory not found!")

    def show_help(self):
        help_text = """Advanced File Compressor Help:

1. Select a file to compress using the Browse button
2. Choose a compression method:
   - ZIP: Standard archive format
   - GZIP: Good for single files
   - BZIP2: Better compression but slower
   - Image Lossy: For JPEG images (quality adjustable)
   - All: Try all applicable methods
3. Adjust quality for image compression (if applicable)
4. Click Start Compression
5. View results and open output folder when done

Note: Some methods may not be suitable for all file types.
"""
        messagebox.showinfo("Help", help_text)

    def show_about(self):
        about_text = """Advanced File Compressor
Version 2.0

A multi-format file compression tool
with support for various algorithms.

© 2023 Compression Tools Inc.
"""
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionGUI(root)
    root.mainloop()