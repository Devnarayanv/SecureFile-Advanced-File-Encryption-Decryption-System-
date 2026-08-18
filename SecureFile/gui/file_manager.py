import os
import sys
import time
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database
from utils.file_utils import format_size
from utils.logger import log_action
from encryption.decryptor import decrypt_file

class PasswordDialog(ctk.CTkToplevel):
    """
    A custom top-level modal dialog to securely prompt for passwords.
    """
    def __init__(self, parent, filename, on_success_callback):
        super().__init__(parent)
        self.parent = parent
        self.filename = filename
        self.on_success_callback = on_success_callback
        
        self.title("Authentication Required")
        self.geometry("360x220")
        self.resizable(False, False)
        self.configure(fg_color="#1e293b")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.init_ui()
        
        # Center the window relative to parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
    def init_ui(self):
        lbl = ctk.CTkLabel(self, text="🔓 Enter Password to Decrypt", font=("Segoe UI", 14, "bold"), text_color="#38bdf8")
        lbl.pack(pady=(20, 5))
        
        file_lbl = ctk.CTkLabel(self, text=f"File: {self.filename}", font=("Segoe UI", 11), text_color="#94a3b8", wraplength=300)
        file_lbl.pack(pady=(0, 15))
        
        self.pw_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", width=260, height=35)
        self.pw_entry.pack(pady=5)
        self.pw_entry.focus()
        self.pw_entry.bind("<Return>", lambda e: self.submit())
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(15, 10))
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="#475569", hover_color="#334155", width=90, height=30, command=self.destroy)
        cancel_btn.pack(side="left", padx=5)
        
        submit_btn = ctk.CTkButton(btn_frame, text="Decrypt", fg_color="#10b981", hover_color="#059669", width=90, height=30, command=self.submit)
        submit_btn.pack(side="right", padx=5)
        
    def submit(self):
        password = self.pw_entry.get()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return
        self.destroy()
        self.on_success_callback(password)

class FileManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#0f172a")
        self.username = username
        
        self.init_ui()
        self.load_files()
        
    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Expand file list
        
        # 1. Header Banner
        title_lbl = ctk.CTkLabel(self, text="Secure Files Manager", font=("Segoe UI", 20, "bold"), text_color="#f8fafc", anchor="w")
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # 2. Search and Control Bar
        control_bar = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        control_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Search Entry
        self.search_entry = ctk.CTkEntry(control_bar, placeholder_text="Search files by name...", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", width=220, height=35)
        self.search_entry.pack(side="left", padx=(15, 10), pady=12)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_files())
        
        # Status Filter
        filter_lbl = ctk.CTkLabel(control_bar, text="Filter:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        filter_lbl.pack(side="left", padx=(10, 2))
        
        self.filter_var = ctk.StringVar(value="All")
        self.filter_dropdown = ctk.CTkOptionMenu(control_bar, values=["All", "ENCRYPTED", "DECRYPTED"], variable=self.filter_var, command=lambda v: self.load_files(), width=120, height=35, fg_color="#0f172a", button_color="#0f172a", button_hover_color="#1e293b", dropdown_fg_color="#0f172a")
        self.filter_dropdown.pack(side="left", padx=(2, 10))
        
        # Sorting
        sort_lbl = ctk.CTkLabel(control_bar, text="Sort by:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        sort_lbl.pack(side="left", padx=(10, 2))
        
        self.sort_var = ctk.StringVar(value="Date (Newest)")
        self.sort_dropdown = ctk.CTkOptionMenu(control_bar, values=["Name (A-Z)", "Name (Z-A)", "Size (Largest)", "Size (Smallest)", "Date (Newest)", "Date (Oldest)"], variable=self.sort_var, command=lambda v: self.load_files(), width=140, height=35, fg_color="#0f172a", button_color="#0f172a", button_hover_color="#1e293b", dropdown_fg_color="#0f172a")
        self.sort_dropdown.pack(side="left", padx=(2, 10))
        
        # Refresh Button
        refresh_btn = ctk.CTkButton(control_bar, text="🔄", width=35, height=35, fg_color="#0f172a", border_color="#334155", border_width=1, hover_color="#0f172a", command=self.load_files)
        refresh_btn.pack(side="right", padx=15)
        
        # 3. Main Scrollable Container for Files List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
    def load_files(self):
        # Clear existing elements
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Headers Layout
        headers_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Columns ratio configuration
        headers_frame.grid_columnconfigure(0, weight=4) # Filename
        headers_frame.grid_columnconfigure(1, weight=2) # Size
        headers_frame.grid_columnconfigure(2, weight=3) # Encryption Date
        headers_frame.grid_columnconfigure(3, weight=2) # Status
        headers_frame.grid_columnconfigure(4, weight=4) # Actions
        
        headers = ["Filename", "Original Size", "Sealed Date", "Status", "Actions"]
        for idx, h in enumerate(headers):
            # Give weight to columns
            col = idx
            lbl = ctk.CTkLabel(headers_frame, text=h, font=("Segoe UI", 11, "bold"), text_color="#94a3b8", anchor="w")
            lbl.grid(row=0, column=col, sticky="ew", padx=5)
            
        # Get files from DB
        raw_files = database.get_all_files()
        
        # Apply Search Filter
        search = self.search_entry.get().strip().lower()
        filtered_files = []
        for f in raw_files:
            if search and search not in f["filename"].lower():
                continue
                
            status_filter = self.filter_var.get()
            if status_filter != "All" and f["status"] != status_filter:
                continue
                
            filtered_files.append(f)
            
        # Apply Sorting
        sort_mode = self.sort_var.get()
        if sort_mode == "Name (A-Z)":
            filtered_files.sort(key=lambda x: x["filename"].lower())
        elif sort_mode == "Name (Z-A)":
            filtered_files.sort(key=lambda x: x["filename"].lower(), reverse=True)
        elif sort_mode == "Size (Largest)":
            filtered_files.sort(key=lambda x: x["original_size"], reverse=True)
        elif sort_mode == "Size (Smallest)":
            filtered_files.sort(key=lambda x: x["original_size"])
        elif sort_mode == "Date (Newest)":
            filtered_files.sort(key=lambda x: x["encryption_date"], reverse=True)
        elif sort_mode == "Date (Oldest)":
            filtered_files.sort(key=lambda x: x["encryption_date"])
            
        if not filtered_files:
            no_files_lbl = ctk.CTkLabel(self.scroll_frame, text="No protected files found matching filters.", font=("Segoe UI", 13), text_color="#64748b")
            no_files_lbl.pack(pady=30)
            return
            
        # Render rows
        for idx, f in enumerate(filtered_files):
            row_bg = "#1e293b" if idx % 2 == 0 else "#16202c"
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=row_bg, corner_radius=6, height=45)
            row_frame.pack(fill="x", padx=5, pady=2)
            row_frame.pack_propagate(False)
            
            row_frame.grid_columnconfigure(0, weight=4)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=2)
            row_frame.grid_columnconfigure(4, weight=4)
            
            # 1. Filename (Truncated if long)
            fname = f["filename"]
            if len(fname) > 28:
                fname_disp = fname[:25] + "..."
            else:
                fname_disp = fname
                
            fname_lbl = ctk.CTkLabel(row_frame, text=fname_disp, font=("Segoe UI", 11, "bold"), text_color="#cbd5e1", anchor="w")
            fname_lbl.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            
            # 2. Size
            sz_lbl = ctk.CTkLabel(row_frame, text=format_size(f["original_size"]), font=("Segoe UI", 11), text_color="#94a3b8", anchor="w")
            sz_lbl.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
            
            # 3. Date
            dt_lbl = ctk.CTkLabel(row_frame, text=f["encryption_date"], font=("Segoe UI", 11), text_color="#94a3b8", anchor="w")
            dt_lbl.grid(row=0, column=2, sticky="ew", padx=5, pady=8)
            
            # 4. Status Badge
            status_text = f["status"]
            status_color = "#34d399" if status_text == "DECRYPTED" else "#38bdf8"
            st_lbl = ctk.CTkLabel(row_frame, text=status_text, font=("Segoe UI", 10, "bold"), text_color=status_color, anchor="w")
            st_lbl.grid(row=0, column=3, sticky="ew", padx=5, pady=8)
            
            # 5. Action Buttons Frame
            act_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_frame.grid(row=0, column=4, sticky="e", padx=10, pady=5)
            
            # Action triggers
            # Open Location button
            loc_btn = ctk.CTkButton(act_frame, text="📁", width=28, height=28, fg_color="#334155", hover_color="#475569", command=lambda path=f["encrypted_path"]: self.open_location(path))
            loc_btn.pack(side="left", padx=2)
            
            # Decrypt button
            if status_text == "ENCRYPTED":
                dec_btn = ctk.CTkButton(act_frame, text="🔓", width=28, height=28, fg_color="#10b981", hover_color="#059669", command=lambda f_rec=f: self.trigger_decryption(f_rec))
                dec_btn.pack(side="left", padx=2)
                
            # Delete button
            del_btn = ctk.CTkButton(act_frame, text="🗑️", width=28, height=28, fg_color="#ef4444", hover_color="#dc2626", command=lambda f_rec=f: self.trigger_delete(f_rec))
            del_btn.pack(side="left", padx=2)
            
    def open_location(self, file_path):
        path = Path(file_path)
        if not path.exists():
            messagebox.showerror("Error", "The file no longer exists at the registered path.")
            return
            
        parent_dir = path.parent
        try:
            if os.name == 'nt':
                # Opens folder and selects the file in Explorer! Very neat Windows command
                os.system(f'explorer /select,"{path}"')
            else:
                os.system(f'open "{parent_dir}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open containing folder:\n{str(e)}")
            
    def trigger_decryption(self, f_record):
        # First, ensure encrypted file is still there
        enc_path = Path(f_record["encrypted_path"])
        if not enc_path.exists():
            messagebox.showerror("Error", f"Encrypted file container not found:\n{f_record['encrypted_path']}")
            return
            
        # Launch password prompt modal
        PasswordDialog(self, f_record["filename"], lambda pw: self.execute_decryption(f_record, pw))
        
    def execute_decryption(self, f_record, password):
        # Open ask folder selection
        dest_dir = filedialog.askdirectory(title="Select Restoration Output Folder")
        if not dest_dir:
            return
            
        # Create progress window
        self.loading_win = ctk.CTkToplevel(self)
        self.loading_win.title("Decrypting...")
        self.loading_win.geometry("300x120")
        self.loading_win.resizable(False, False)
        self.loading_win.configure(fg_color="#1e293b")
        self.loading_win.transient(self)
        self.loading_win.grab_set()
        
        # Center loader
        self.loading_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - self.loading_win.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - self.loading_win.winfo_height()) // 2
        self.loading_win.geometry(f"+{x}+{y}")
        
        loader_lbl = ctk.CTkLabel(self.loading_win, text="🔓 Restoring Data Content...", font=("Segoe UI", 12, "bold"), text_color="#cbd5e1")
        loader_lbl.pack(pady=(20, 10))
        
        self.load_bar = ctk.CTkProgressBar(self.loading_win, fg_color="#0f172a", progress_color="#10b981", width=220)
        self.load_bar.pack(pady=5)
        self.load_bar.set(0)
        
        # Threading details
        self.dec_error = None
        self.dec_result = None
        self.start_t = time.time()
        
        def decrypt_thread():
            try:
                def progress_cb(prog, status):
                    self.after(0, lambda: self.load_bar.set(prog))
                res = decrypt_file(
                    encrypted_path=f_record["encrypted_path"],
                    dest_dir=dest_dir,
                    password=password,
                    progress_callback=progress_cb
                )
                self.dec_result = res
            except Exception as e:
                self.dec_error = e
                
        t = threading.Thread(target=decrypt_thread, daemon=True)
        t.start()
        
        # Poll completion
        self.poll_manager_decryption(t, f_record)
        
    def poll_manager_decryption(self, thread, f_record):
        if thread.is_alive():
            self.after(100, lambda: self.poll_manager_decryption(thread, f_record))
        else:
            # Close dialog
            self.loading_win.destroy()
            
            duration = time.time() - self.start_t
            src_name = f_record["filename"]
            src_size = f_record["original_size"]
            
            if self.dec_error:
                log_action(self.username, src_name, "DECRYPT", src_size, "FAILED", duration)
                messagebox.showerror("Error", f"Decryption failed:\n{str(self.dec_error)}")
            else:
                orig_name, restored_path, orig_size = self.dec_result
                # Update DB record
                database.update_file_status(f_record["encrypted_path"], "DECRYPTED")
                log_action(self.username, orig_name, "DECRYPT", orig_size, "SUCCESS", duration)
                
                messagebox.showinfo("Success", f"File successfully decrypted!\nRestored: {restored_path}")
                self.load_files()
                
    def trigger_delete(self, f_record):
        app_settings = database.get_settings()
        confirm = app_settings.get("confirm_delete", "True") == "True"
        
        if confirm:
            ans = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete this file registration?\n\nFile: {f_record['filename']}\n\n"
                "Note: This will delete the physical encrypted .secure container on disk!"
            )
            if not ans:
                return
                
        # Perform physical deletion
        enc_path = Path(f_record["encrypted_path"])
        if enc_path.exists():
            try:
                os.remove(enc_path)
            except Exception as e:
                messagebox.showerror("IO Error", f"Failed to delete the container file on disk:\n{str(e)}\n\nDatabase registration will still be updated.")
                
        # Update database status to deleted
        database.update_file_status(f_record["encrypted_path"], "DELETED")
        
        # Log action
        log_action(self.username, f_record["filename"], "DELETE", f_record["original_size"], "SUCCESS")
        
        messagebox.showinfo("Deleted", "File registration and container deleted successfully.")
        self.load_files()
