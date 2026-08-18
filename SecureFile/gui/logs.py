import csv
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database
from utils.file_utils import format_size

class LogsFrame(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#0f172a")
        self.username = username
        self.init_ui()
        self.load_logs()
        
    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Expand scroll area
        
        # 1. Header Banner
        title_lbl = ctk.CTkLabel(self, text="Activity Audit Logs", font=("Segoe UI", 20, "bold"), text_color="#f8fafc", anchor="w")
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # 2. Control Bar
        control_bar = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        control_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Search Entry
        self.search_entry = ctk.CTkEntry(control_bar, placeholder_text="Search logs by file / user...", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", width=220, height=35)
        self.search_entry.pack(side="left", padx=(15, 10), pady=12)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_logs())
        
        # Operation Filter
        filter_lbl = ctk.CTkLabel(control_bar, text="Operation:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        filter_lbl.pack(side="left", padx=(10, 2))
        
        self.filter_var = ctk.StringVar(value="All")
        self.filter_dropdown = ctk.CTkOptionMenu(control_bar, values=["All", "ENCRYPT", "DECRYPT", "DELETE", "LOGIN", "LOGIN FAILED"], variable=self.filter_var, command=lambda v: self.load_logs(), width=120, height=35, fg_color="#0f172a", button_color="#0f172a", button_hover_color="#1e293b", dropdown_fg_color="#0f172a")
        self.filter_dropdown.pack(side="left", padx=(2, 10))
        
        # Export CSV Button
        csv_btn = ctk.CTkButton(control_bar, text="Export CSV", fg_color="#3b82f6", hover_color="#2563eb", width=95, height=35, font=("Segoe UI", 11, "bold"), command=self.export_csv)
        csv_btn.pack(side="right", padx=15)
        
        # Clear Logs Button
        clear_btn = ctk.CTkButton(control_bar, text="Clear Logs", fg_color="#ef4444", hover_color="#dc2626", width=95, height=35, font=("Segoe UI", 11, "bold"), command=self.confirm_clear_logs)
        clear_btn.pack(side="right", padx=5)
        
        # 3. Main Scrollable Container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
    def load_logs(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Headers Layout
        headers_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Config columns width ratios
        headers_frame.grid_columnconfigure(0, weight=3) # Timestamp
        headers_frame.grid_columnconfigure(1, weight=2) # User
        headers_frame.grid_columnconfigure(2, weight=2) # Operation
        headers_frame.grid_columnconfigure(3, weight=4) # Target File
        headers_frame.grid_columnconfigure(4, weight=2) # Size
        headers_frame.grid_columnconfigure(5, weight=2) # Result
        headers_frame.grid_columnconfigure(6, weight=2) # Time taken
        
        headers = ["Timestamp", "User", "Operation", "Target File", "Size", "Result", "Duration"]
        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(headers_frame, text=h, font=("Segoe UI", 11, "bold"), text_color="#94a3b8", anchor="w")
            lbl.grid(row=0, column=idx, sticky="ew", padx=5)
            
        # Retrieve logs
        search_query = self.search_entry.get().strip()
        op_filter = self.filter_var.get()
        self.loaded_logs_data = database.get_activity_logs(search_query, op_filter)
        
        if not self.loaded_logs_data:
            no_logs = ctk.CTkLabel(self.scroll_frame, text="No audit records found matching criteria.", font=("Segoe UI", 13), text_color="#64748b")
            no_logs.pack(pady=30)
            return
            
        # Render rows
        for idx, log in enumerate(self.loaded_logs_data):
            row_bg = "#1e293b" if idx % 2 == 0 else "#16202c"
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=row_bg, corner_radius=6, height=45)
            row_frame.pack(fill="x", padx=5, pady=2)
            row_frame.pack_propagate(False)
            
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=4)
            row_frame.grid_columnconfigure(4, weight=2)
            row_frame.grid_columnconfigure(5, weight=2)
            row_frame.grid_columnconfigure(6, weight=2)
            
            # Formatted values
            timestamp = log["timestamp"]
            user = log["username"]
            op = log["operation"]
            
            filename = log["filename"] if log["filename"] else "-"
            if len(filename) > 24:
                filename_disp = filename[:21] + "..."
            else:
                filename_disp = filename
                
            size = format_size(log["original_size"]) if log["original_size"] is not None else "-"
            result = log["result"]
            duration = f"{log['duration']:.2f}s" if log["duration"] > 0 else "-"
            
            ctk.CTkLabel(row_frame, text=timestamp, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            ctk.CTkLabel(row_frame, text=user, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=1, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(row_frame, text=op, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=2, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(row_frame, text=filename_disp, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=3, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(row_frame, text=size, font=("Segoe UI", 11), text_color="#94a3b8", anchor="w").grid(row=0, column=4, sticky="ew", padx=5, pady=8)
            
            res_color = "#34d399" if result == "SUCCESS" else "#f87171"
            ctk.CTkLabel(row_frame, text=result, font=("Segoe UI", 10, "bold"), text_color=res_color, anchor="w").grid(row=0, column=5, sticky="ew", padx=5, pady=8)
            ctk.CTkLabel(row_frame, text=duration, font=("Segoe UI", 11), text_color="#94a3b8", anchor="w").grid(row=0, column=6, sticky="ew", padx=5, pady=8)
            
    def confirm_clear_logs(self):
        ans = messagebox.askyesno("Confirm Action", "Are you sure you want to delete all activity audit logs permanently?\nThis action cannot be undone.")
        if ans:
            database.clear_activity_logs()
            self.load_logs()
            messagebox.showinfo("Success", "Logs database cleared successfully.")
            
    def export_csv(self):
        if not self.loaded_logs_data:
            messagebox.showwarning("Empty Dataset", "There are no logs loaded to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv")],
            title="Export Audit Logs"
        )
        if not file_path:
            return
            
        try:
            headers = ["ID", "Timestamp", "Username", "Filename", "Operation", "Size (bytes)", "Result", "Duration (seconds)"]
            
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for log in self.loaded_logs_data:
                    writer.writerow([
                        log.get("id"),
                        log.get("timestamp"),
                        log.get("username"),
                        log.get("filename", ""),
                        log.get("operation"),
                        log.get("original_size", ""),
                        log.get("result"),
                        log.get("duration", 0.0)
                    ])
                    
            messagebox.showinfo("Export Successful", f"Audit logs successfully saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("IO Error", f"Failed to write CSV file:\n{str(e)}")
