import time
import sys
import customtkinter as ctk
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from security import authentication
from database import database
from utils.logger import log_action

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="#0f172a") # Slate 900
        self.parent = parent
        self.on_login_success = on_login_success
        
        # Load settings
        self.app_settings = database.get_settings()
        
        self.init_ui()
        
    def init_ui(self):
        # Configure grid expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main Card Frame
        card = ctk.CTkFrame(self, width=400, height=500, corner_radius=16, fg_color="#1e293b", border_color="#334155", border_width=1)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        
        card.grid_columnconfigure(0, weight=1)
        
        # Header Lock Emoji
        lock_emoji = ctk.CTkLabel(card, text="🔐", font=("Segoe UI Emoji", 48))
        lock_emoji.grid(row=0, column=0, pady=(40, 10))
        
        # Title
        title_label = ctk.CTkLabel(card, text="SECUREFILE", text_color="#38bdf8", font=("Segoe UI", 28, "bold"))
        title_label.grid(row=1, column=0, pady=(0, 2))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(card, text="Advanced File Encryption & Decryption System", text_color="#94a3b8", font=("Segoe UI", 12))
        subtitle_label.grid(row=2, column=0, pady=(0, 25))
        
        # Username Entry
        self.username_entry = ctk.CTkEntry(card, width=280, height=40, placeholder_text="Username", fg_color="#0f172a", text_color="#f8fafc", border_color="#334155")
        self.username_entry.grid(row=3, column=0, pady=10)
        
        # Prepopulate username if remembered
        saved_username = self.app_settings.get("remembered_username", "")
        if saved_username:
            self.username_entry.insert(0, saved_username)
            
        # Password Entry
        self.password_entry = ctk.CTkEntry(card, width=280, height=40, placeholder_text="Password", show="*", fg_color="#0f172a", text_color="#f8fafc", border_color="#334155")
        self.password_entry.grid(row=4, column=0, pady=10)
        
        # Entry Action bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Options row (Show Password & Remember Me)
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.grid(row=5, column=0, pady=5, sticky="ew", padx=60)
        
        self.show_password_var = ctk.StringVar(value="off")
        self.show_password_cb = ctk.CTkCheckBox(options_frame, text="Show", variable=self.show_password_var, onvalue="on", offvalue="off", command=self.toggle_password, font=("Segoe UI", 11), text_color="#94a3b8", checkbox_width=16, checkbox_height=16, border_width=1)
        self.show_password_cb.pack(side="left")
        
        remember_checked = "on" if saved_username else "off"
        self.remember_var = ctk.StringVar(value=remember_checked)
        self.remember_cb = ctk.CTkCheckBox(options_frame, text="Remember Me", variable=self.remember_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), text_color="#94a3b8", checkbox_width=16, checkbox_height=16, border_width=1)
        self.remember_cb.pack(side="right")
        
        # Error / Feedback Message Label
        self.error_label = ctk.CTkLabel(card, text="", text_color="#ef4444", font=("Segoe UI", 12), wraplength=280)
        self.error_label.grid(row=6, column=0, pady=(10, 5))
        
        # Login Button
        self.login_btn = ctk.CTkButton(card, text="LOGIN", width=280, height=40, corner_radius=8, fg_color="#3b82f6", hover_color="#2563eb", text_color="#ffffff", font=("Segoe UI", 14, "bold"), command=self.handle_login)
        self.login_btn.grid(row=7, column=0, pady=(10, 20))
        
        # Check initial lockout
        self.check_lockout()
        
    def toggle_password(self):
        if self.show_password_var.get() == "on":
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
            
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Please enter both username and password.")
            return
            
        success, message = authentication.authenticate(username, password)
        
        if success:
            # Save or remove remembered username
            if self.remember_var.get() == "on":
                database.update_setting("remembered_username", username)
            else:
                database.update_setting("remembered_username", "")
                
            # Log action
            log_action(username, None, "LOGIN", None, "SUCCESS")
            
            # Callback to main view
            self.on_login_success(username)
        else:
            # Log failure
            log_action(username or "unknown", None, "LOGIN FAILED", None, "FAILED")
            self.show_error(message)
            self.check_lockout()
            
    def show_error(self, message):
        self.error_label.configure(text=message)
        
    def check_lockout(self):
        username = self.username_entry.get().strip()
        if not username:
            return
            
        user = database.get_user(username)
        if user:
            lockout_until = user["lockout_until"]
            current_time = time.time()
            if lockout_until and lockout_until > current_time:
                self.lockout_remaining = int(lockout_until - current_time)
                self.disable_login_for_lockout()
                
    def disable_login_for_lockout(self):
        self.login_btn.configure(state="disabled", fg_color="#475569")
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.update_lockout_countdown()
        
    def update_lockout_countdown(self):
        if self.lockout_remaining > 0:
            self.show_error(f"Brute force detected. Locked out for {self.lockout_remaining}s.")
            self.lockout_remaining -= 1
            self.after(1000, self.update_lockout_countdown)
        else:
            self.show_error("")
            self.login_btn.configure(state="normal", fg_color="#3b82f6")
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
