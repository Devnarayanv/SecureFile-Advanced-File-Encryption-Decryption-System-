import sys
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from encryption.decryptor import decrypt_file
from encryption.encryptor import OperationCancelled
from database import database
from utils.file_utils import format_size, get_file_permissions
from utils.logger import log_action

class DecryptFrame(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#0f172a")
        self.username = username
        
        self.selected_file_path = None
        self.dest_dir_path = None
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.start_time = 0.0
        
        self.init_ui()
        
    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Title Banner
        title_lbl = ctk.CTkLabel(self, text="File Decryption Panel", font=("Segoe UI", 20, "bold"), text_color="#f8fafc", anchor="w")
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Form Container
        form_frame = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        # 1. File Selection Row
        file_select_lbl = ctk.CTkLabel(form_frame, text="Select Encrypted .secure Container:", font=("Segoe UI", 12, "bold"), text_color="#cbd5e1", anchor="w")
        file_select_lbl.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        file_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        file_row.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        file_row.grid_columnconfigure(0, weight=1)
        
        self.file_path_entry = ctk.CTkEntry(file_row, placeholder_text="No .secure file selected...", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=35)
        self.file_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.file_path_entry.configure(state="disabled")
        
        browse_btn = ctk.CTkButton(file_row, text="Browse File", fg_color="#3b82f6", hover_color="#2563eb", width=110, height=35, command=self.browse_file)
        browse_btn.grid(row=0, column=1)
        
        # 2. File Metadata Panel (collapsible card)
        self.meta_frame = ctk.CTkFrame(form_frame, fg_color="#0f172a", border_color="#1e293b", border_width=1, corner_radius=8)
        
        self.meta_title = ctk.CTkLabel(self.meta_frame, text="Container Properties & Encryption Details", font=("Segoe UI", 11, "bold"), text_color="#38bdf8")
        self.meta_title.pack(anchor="w", padx=15, pady=(8, 2))
        
        self.meta_details = ctk.CTkLabel(self.meta_frame, text="", font=("Courier New", 11), text_color="#cbd5e1", justify="left", anchor="w")
        self.meta_details.pack(anchor="w", padx=15, pady=(0, 8))
        
        # 3. Output Directory Selection Row
        dest_select_lbl = ctk.CTkLabel(form_frame, text="Select Restoration Destination Folder:", font=("Segoe UI", 12, "bold"), text_color="#cbd5e1", anchor="w")
        dest_select_lbl.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="w")
        
        dest_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        dest_row.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        dest_row.grid_columnconfigure(0, weight=1)
        
        self.dest_path_entry = ctk.CTkEntry(dest_row, placeholder_text="Defaults to container folder...", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=35)
        self.dest_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.dest_path_entry.configure(state="disabled")
        
        browse_dest_btn = ctk.CTkButton(dest_row, text="Choose Folder", fg_color="#3b82f6", hover_color="#2563eb", width=110, height=35, command=self.browse_dest_dir)
        browse_dest_btn.grid(row=0, column=1)
        
        # 4. Password Input Field
        pw_title = ctk.CTkLabel(form_frame, text="Decryption Password:", font=("Segoe UI", 12, "bold"), text_color="#cbd5e1", anchor="w")
        pw_title.grid(row=5, column=0, padx=20, pady=(15, 5), sticky="w")
        
        pw_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        pw_grid.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        pw_grid.grid_columnconfigure(0, weight=1)
        
        self.pw_entry = ctk.CTkEntry(pw_grid, placeholder_text="Password", show="*", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=38)
        self.pw_entry.grid(row=0, column=0, sticky="ew")
        
        self.show_pw_var = ctk.StringVar(value="off")
        show_pw_cb = ctk.CTkCheckBox(form_frame, text="Show Password", variable=self.show_pw_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), text_color="#94a3b8", command=self.toggle_pw_visibility, checkbox_width=16, checkbox_height=16, border_width=1)
        show_pw_cb.grid(row=7, column=0, padx=20, pady=(5, 15), sticky="w")
        
        # 5. Action Row (Decrypt / Cancel / Progress / Diagnostics)
        self.op_frame = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        self.op_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.op_frame.grid_columnconfigure(0, weight=1)
        
        # Progress section
        self.progress_bar = ctk.CTkProgressBar(self.op_frame, fg_color="#0f172a", progress_color="#10b981", height=8)
        self.progress_bar.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 2), sticky="ew")
        self.progress_bar.set(0)
        
        self.status_lbl = ctk.CTkLabel(self.op_frame, text="Status: Ready", font=("Segoe UI", 12, "bold"), text_color="#94a3b8")
        self.status_lbl.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Control Buttons
        btn_frame = ctk.CTkFrame(self.op_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="ew")
        
        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel Operation", fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", state="disabled", font=("Segoe UI", 12, "bold"), command=self.cancel_decryption)
        self.cancel_btn.pack(side="right", padx=5)
        
        self.decrypt_btn = ctk.CTkButton(btn_frame, text="Decrypt File", fg_color="#10b981", hover_color="#059669", text_color="#ffffff", font=("Segoe UI", 12, "bold"), command=self.start_decryption)
        self.decrypt_btn.pack(side="right", padx=5)
        
        # OS Diagnostics
        self.diag_frame = ctk.CTkFrame(self.op_frame, fg_color="#0f172a", corner_radius=8)
        self.diag_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
        
        self.diag_lbl = ctk.CTkLabel(self.diag_frame, text="Process: Idle  |  Worker: Idle  |  Thread: None", font=("Segoe UI", 11), text_color="#64748b")
        self.diag_lbl.pack(padx=15, pady=8, anchor="w")
        
    def toggle_pw_visibility(self):
        show_val = "" if self.show_pw_var.get() == "on" else "*"
        self.pw_entry.configure(show=show_val)
        
    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("SecureFile Containers", "*.secure")])
        if not path:
            return
            
        self.selected_file_path = path
        
        # Update path entry
        self.file_path_entry.configure(state="normal")
        self.file_path_entry.delete(0, ctk.END)
        self.file_path_entry.insert(0, path)
        self.file_path_entry.configure(state="disabled")
        
        # Retrieve metadata
        p = Path(path)
        size_str = format_size(p.stat().st_size)
        octal_perm, readable_perm = get_file_permissions(path)
        
        meta_txt = (
            f"• Container   : {p.name}\n"
            f"• Location    : {p.parent}\n"
            f"• Sealed Size : {size_str} ({p.stat().st_size} bytes)\n"
            f"• Permissions : UNIX Octal {octal_perm} ({readable_perm})"
        )
        
        self.meta_details.configure(text=meta_txt)
        self.meta_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Set default destination folder as parent of this file
        if not self.dest_dir_path:
            self.dest_path_entry.configure(state="normal")
            self.dest_path_entry.delete(0, ctk.END)
            self.dest_path_entry.insert(0, str(p.parent))
            self.dest_path_entry.configure(state="disabled")
            
    def browse_dest_dir(self):
        path = filedialog.askdirectory()
        if not path:
            return
            
        self.dest_dir_path = path
        self.dest_path_entry.configure(state="normal")
        self.dest_path_entry.delete(0, ctk.END)
        self.dest_path_entry.insert(0, path)
        self.dest_path_entry.configure(state="disabled")
        
    def start_decryption(self):
        if not self.selected_file_path:
            messagebox.showerror("Error", "Please select a .secure file to decrypt first.")
            return
            
        pw = self.pw_entry.get()
        if not pw:
            messagebox.showerror("Error", "Please enter the decryption password.")
            return
            
        # Get settings for default decrypt path
        app_settings = database.get_settings()
        dest_dir = self.dest_dir_path
        if not dest_dir:
            dest_dir = app_settings.get("default_decrypt_dir", "").strip()
        if not dest_dir:
            dest_dir = str(Path(self.selected_file_path).parent)
            
        if not Path(dest_dir).exists():
            messagebox.showerror("Error", f"Restoration destination folder does not exist: {dest_dir}")
            return
            
        # UI resets
        self.decrypt_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_lbl.configure(text="Status: Initiating...", text_color="#38bdf8")
        
        self.stop_event.clear()
        self.start_time = time.time()
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self.run_decryption_worker,
            args=(self.selected_file_path, dest_dir, pw),
            daemon=True
        )
        self.worker_thread.start()
        
        # Update diagnostics display
        self.diag_lbl.configure(
            text=f"Process: BUSY  |  Worker: Decryption Worker  |  Thread ID: {self.worker_thread.ident or 'Starting...'}",
            text_color="#38bdf8"
        )
        
        # Monitor thread
        self.poll_decryption_progress()
        
    def run_decryption_worker(self, src, dest, pw):
        self.operation_error = None
        self.result_data = None
        
        def inner_callback(progress, status):
            self.after(0, lambda: self.update_progress_ui(progress, status))
            
        try:
            orig_name, restored_path, orig_size = decrypt_file(
                encrypted_path=src,
                dest_dir=dest,
                password=pw,
                progress_callback=inner_callback,
                stop_event=self.stop_event
            )
            self.result_data = (orig_name, restored_path, orig_size)
        except Exception as e:
            self.operation_error = e
            
    def update_progress_ui(self, progress, status):
        self.progress_bar.set(progress)
        self.status_lbl.configure(text=f"Status: {status}", text_color="#38bdf8")
        
    def poll_decryption_progress(self):
        if self.worker_thread and self.worker_thread.is_alive():
            self.after(100, self.poll_decryption_progress)
        else:
            self.decrypt_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            
            duration = time.time() - self.start_time
            src_name = Path(self.selected_file_path).name
            src_size = Path(self.selected_file_path).stat().st_size
            
            if self.operation_error:
                if isinstance(self.operation_error, OperationCancelled):
                    self.status_lbl.configure(text="Status: Cancelled", text_color="#ef4444")
                    self.diag_lbl.configure(text="Process: Idle  |  Worker: Idle  |  Thread: None", text_color="#64748b")
                    log_action(self.username, src_name, "DECRYPT", src_size, "FAILED", duration)
                    messagebox.showwarning("Cancelled", "File decryption was cancelled by user.")
                else:
                    self.status_lbl.configure(text="Status: Failed", text_color="#ef4444")
                    self.diag_lbl.configure(text="Process: Idle  |  Worker: Idle  |  Thread: None", text_color="#64748b")
                    log_action(self.username, src_name, "DECRYPT", src_size, "FAILED", duration)
                    messagebox.showerror("Error", f"Decryption failed:\n{str(self.operation_error)}")
            else:
                # Success
                orig_name, restored_path, orig_size = self.result_data
                self.progress_bar.set(1.0)
                self.status_lbl.configure(text="Status: Success!", text_color="#10b981")
                self.diag_lbl.configure(text="Process: Idle  |  Worker: Idle  |  Thread: None", text_color="#64748b")
                
                # Update file status in database to DECRYPTED
                database.update_file_status(self.selected_file_path, "DECRYPTED")
                
                # Log operation
                log_action(self.username, orig_name, "DECRYPT", orig_size, "SUCCESS", duration)
                
                messagebox.showinfo("Success", f"File decrypted successfully!\nRestored: {restored_path}")
                
                # Clean inputs
                self.pw_entry.delete(0, ctk.END)
                
    def cancel_decryption(self):
        self.stop_event.set()
        self.status_lbl.configure(text="Status: Cancelling...", text_color="#ef4444")
        self.cancel_btn.configure(state="disabled")
