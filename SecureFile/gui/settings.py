import sys
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database
from security.password_manager import hash_password, verify_password
from utils.logger import log_action

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, username, change_theme_callback=None):
        super().__init__(parent, fg_color="#0f172a")
        self.username = username
        self.change_theme_callback = change_theme_callback
        
        self.app_settings = database.get_settings()
        self.init_ui()
        
    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Scrollable area expands
        
        # We wrap everything in a scrollable frame since settings has many sections
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid_columnconfigure(0, weight=1)
        
        # Title Banner
        title_lbl = ctk.CTkLabel(scroll, text="Application Settings & Customizations", font=("Segoe UI", 20, "bold"), text_color="#f8fafc", anchor="w")
        title_lbl.pack(fill="x", padx=15, pady=(10, 15))
        
        # =====================================================================
        # SECTION 1: CHANGE PASSWORD
        # =====================================================================
        pw_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        pw_card.pack(fill="x", padx=15, pady=8)
        
        pw_title = ctk.CTkLabel(pw_card, text="🔑 Rotate Account Access Password", font=("Segoe UI", 14, "bold"), text_color="#38bdf8", anchor="w")
        pw_title.pack(fill="x", padx=15, pady=(15, 10))
        
        pw_grid = ctk.CTkFrame(pw_card, fg_color="transparent")
        pw_grid.pack(fill="x", padx=15, pady=5)
        pw_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.cur_pw = ctk.CTkEntry(pw_grid, placeholder_text="Current Password", show="*", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=35)
        self.cur_pw.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.new_pw = ctk.CTkEntry(pw_grid, placeholder_text="New Password", show="*", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=35)
        self.new_pw.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.confirm_new_pw = ctk.CTkEntry(pw_grid, placeholder_text="Confirm New Password", show="*", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=35)
        self.confirm_new_pw.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Action Row
        pw_act_row = ctk.CTkFrame(pw_card, fg_color="transparent")
        pw_act_row.pack(fill="x", padx=15, pady=(10, 15))
        
        self.show_pw_var = ctk.StringVar(value="off")
        show_pw_cb = ctk.CTkCheckBox(pw_act_row, text="Show Passwords", variable=self.show_pw_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), text_color="#94a3b8", command=self.toggle_pw_visibility, checkbox_width=16, checkbox_height=16, border_width=1)
        show_pw_cb.pack(side="left", pady=5)
        
        change_pw_btn = ctk.CTkButton(pw_act_row, text="Update Password", fg_color="#3b82f6", hover_color="#2563eb", font=("Segoe UI", 12, "bold"), width=130, height=35, command=self.change_password)
        change_pw_btn.pack(side="right")
        
        # =====================================================================
        # SECTION 2: UI PREFERENCES (THEME)
        # =====================================================================
        ui_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        ui_card.pack(fill="x", padx=15, pady=8)
        
        ui_title = ctk.CTkLabel(ui_card, text="⚙️ Graphic Interface Preferences", font=("Segoe UI", 14, "bold"), text_color="#38bdf8", anchor="w")
        ui_title.pack(fill="x", padx=15, pady=(15, 10))
        
        theme_row = ctk.CTkFrame(ui_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=15, pady=(5, 15))
        
        theme_lbl = ctk.CTkLabel(theme_row, text="Interface Appearance Theme Mode:", font=("Segoe UI", 12), text_color="#cbd5e1")
        theme_lbl.pack(side="left")
        
        current_theme = self.app_settings.get("theme", "Dark")
        self.theme_dropdown = ctk.CTkOptionMenu(theme_row, values=["Dark", "Light", "System"], command=self.change_theme, fg_color="#0f172a", button_color="#0f172a", button_hover_color="#1e293b", dropdown_fg_color="#0f172a", width=120, height=35)
        self.theme_dropdown.set(current_theme)
        self.theme_dropdown.pack(side="right")
        
        # =====================================================================
        # SECTION 3: DIRECTORY CONFIGURATIONS
        # =====================================================================
        dir_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        dir_card.pack(fill="x", padx=15, pady=8)
        
        dir_title = ctk.CTkLabel(dir_card, text="📁 Default Storage Directories", font=("Segoe UI", 14, "bold"), text_color="#38bdf8", anchor="w")
        dir_title.pack(fill="x", padx=15, pady=(15, 10))
        
        # Encryption Folder Path Selection
        enc_lbl = ctk.CTkLabel(dir_card, text="Default Encryption Directory Output:", font=("Segoe UI", 12), text_color="#cbd5e1", anchor="w")
        enc_lbl.pack(fill="x", padx=15, pady=(5, 2))
        
        enc_row = ctk.CTkFrame(dir_card, fg_color="transparent")
        enc_row.pack(fill="x", padx=15, pady=(0, 10))
        enc_row.grid_columnconfigure(0, weight=1)
        
        self.enc_path_entry = ctk.CTkEntry(enc_row, placeholder_text="Defaults to target file folder", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=32)
        self.enc_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.enc_path_entry.insert(0, self.app_settings.get("default_encrypt_dir", ""))
        self.enc_path_entry.configure(state="disabled")
        
        enc_browse = ctk.CTkButton(enc_row, text="Choose Path", fg_color="#3b82f6", hover_color="#2563eb", width=100, height=32, command=lambda: self.browse_directory("default_encrypt_dir", self.enc_path_entry))
        enc_browse.grid(row=0, column=1)
        
        # Decryption Folder Path Selection
        dec_lbl = ctk.CTkLabel(dir_card, text="Default Decryption Directory Output:", font=("Segoe UI", 12), text_color="#cbd5e1", anchor="w")
        dec_lbl.pack(fill="x", padx=15, pady=(5, 2))
        
        dec_row = ctk.CTkFrame(dir_card, fg_color="transparent")
        dec_row.pack(fill="x", padx=15, pady=(0, 15))
        dec_row.grid_columnconfigure(0, weight=1)
        
        self.dec_path_entry = ctk.CTkEntry(dec_row, placeholder_text="Defaults to container folder", fg_color="#0f172a", border_color="#334155", text_color="#f8fafc", height=32)
        self.dec_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.dec_path_entry.insert(0, self.app_settings.get("default_decrypt_dir", ""))
        self.dec_path_entry.configure(state="disabled")
        
        dec_browse = ctk.CTkButton(dec_row, text="Choose Path", fg_color="#3b82f6", hover_color="#2563eb", width=100, height=32, command=lambda: self.browse_directory("default_decrypt_dir", self.dec_path_entry))
        dec_browse.grid(row=0, column=1)
        
        # =====================================================================
        # SECTION 4: SECURITY SWITCHES & DATA BACKUP
        # =====================================================================
        sec_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        sec_card.pack(fill="x", padx=15, pady=8)
        
        sec_title = ctk.CTkLabel(sec_card, text="🛡️ Security Preferences & Database Maintenance", font=("Segoe UI", 14, "bold"), text_color="#38bdf8", anchor="w")
        sec_title.pack(fill="x", padx=15, pady=(15, 10))
        
        # Confirm Deletion Switch
        confirm_checked = self.app_settings.get("confirm_delete", "True") == "True"
        self.confirm_var = ctk.StringVar(value="on" if confirm_checked else "off")
        confirm_switch = ctk.CTkSwitch(sec_card, text="Prompt for confirmation before deleting secure containers", variable=self.confirm_var, onvalue="on", offvalue="off", command=lambda: self.update_switch("confirm_delete", self.confirm_var), font=("Segoe UI", 12), text_color="#cbd5e1", progress_color="#10b981")
        confirm_switch.pack(anchor="w", padx=15, pady=5)
        
        # Auto-Clear Temp Switch
        clear_checked = self.app_settings.get("auto_clear_temp", "True") == "True"
        self.clear_var = ctk.StringVar(value="on" if clear_checked else "off")
        clear_switch = ctk.CTkSwitch(sec_card, text="Automatically clean up aborted / incomplete decryption fragments", variable=self.clear_var, onvalue="on", offvalue="off", command=lambda: self.update_switch("auto_clear_temp", self.clear_var), font=("Segoe UI", 12), text_color="#cbd5e1", progress_color="#10b981")
        clear_switch.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Database Backup Option
        backup_separator = ctk.CTkFrame(sec_card, height=1, fg_color="#334155")
        backup_separator.pack(fill="x", padx=15, pady=5)
        
        backup_row = ctk.CTkFrame(sec_card, fg_color="transparent")
        backup_row.pack(fill="x", padx=15, pady=(10, 15))
        
        backup_lbl = ctk.CTkLabel(backup_row, text="Create a backup image of the SQLite database:", font=("Segoe UI", 12), text_color="#cbd5e1")
        backup_lbl.pack(side="left")
        
        backup_btn = ctk.CTkButton(backup_row, text="Export Database", fg_color="#10b981", hover_color="#059669", font=("Segoe UI", 12, "bold"), width=130, height=35, command=self.export_database_backup)
        backup_btn.pack(side="right")
        
    def toggle_pw_visibility(self):
        show_val = "" if self.show_pw_var.get() == "on" else "*"
        self.cur_pw.configure(show=show_val)
        self.new_pw.configure(show=show_val)
        self.confirm_new_pw.configure(show=show_val)
        
    def change_password(self):
        username = self.username
        cur = self.cur_pw.get()
        new = self.new_pw.get()
        confirm = self.confirm_new_pw.get()
        
        if not cur or not new or not confirm:
            messagebox.showerror("Error", "All password fields are required.")
            return
            
        user = database.get_user(username)
        if not user or not verify_password(cur, user["password_hash"]):
            messagebox.showerror("Error", "Current password is incorrect.")
            return
            
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match.")
            return
            
        # Update password in DB
        hashed = hash_password(new)
        database.change_user_password(username, hashed)
        log_action(username, None, "LOGIN", None, "SUCCESS") # password rotation logs
        
        messagebox.showinfo("Success", "Password updated successfully!")
        
        # Clear fields
        self.cur_pw.delete(0, ctk.END)
        self.new_pw.delete(0, ctk.END)
        self.confirm_new_pw.delete(0, ctk.END)
        
    def change_theme(self, mode):
        database.update_setting("theme", mode)
        ctk.set_appearance_mode(mode)
        if self.change_theme_callback:
            self.change_theme_callback(mode)
            
    def browse_directory(self, setting_key, entry_widget):
        path = filedialog.askdirectory()
        if not path:
            return
            
        database.update_setting(setting_key, path)
        
        entry_widget.configure(state="normal")
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, path)
        entry_widget.configure(state="disabled")
        
    def update_switch(self, setting_key, var):
        state_str = "True" if var.get() == "on" else "False"
        database.update_setting(setting_key, state_str)
        
    def export_database_backup(self):
        src_db = database.DB_PATH
        if not src_db.exists():
            messagebox.showerror("Error", "Source database does not exist.")
            return
            
        dest_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            title="Export Database Backup",
            initialfile="securefile_backup.db"
        )
        if not dest_path:
            return
            
        try:
            shutil.copy2(src_db, dest_path)
            messagebox.showinfo("Backup Successful", f"Database backed up successfully to:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("IO Error", f"Failed to export database backup:\n{str(e)}")
