import sys
import customtkinter as ctk
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent))

from database import database
from gui.login import LoginFrame
from gui.dashboard import DashboardFrame
from gui.encrypt import EncryptFrame
from gui.decrypt import DecryptFrame
from gui.file_manager import FileManagerFrame
from gui.logs import LogsFrame
from gui.settings import SettingsFrame
from gui.about import AboutFrame

class SecureFileApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Initialize SQLite Database Tables
        database.init_db()
        
        # 2. Configure Main Application Window
        self.title("SecureFile – Advanced File Encryption & Decryption System")
        self.geometry("1060x680")
        self.minsize(980, 600)
        
        # 3. Load Theme from Database
        app_settings = database.get_settings()
        theme_mode = app_settings.get("theme", "Dark")
        ctk.set_appearance_mode(theme_mode)
        ctk.set_default_color_theme("blue") # Set default theme accents
        
        self.current_user = None
        self.current_page_frame = None
        self.sidebar_buttons = {}
        
        # 4. Grid Expansion Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Launch login frame
        self.show_login_screen()
        
    def show_login_screen(self):
        # Clear screen of any layout widgets if logged out
        for w in self.winfo_children():
            w.destroy()
            
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_login_success(self, username):
        self.current_user = username
        self.login_frame.destroy()
        
        # Build Main Workspace Frame
        self.build_workspace()
        
    def build_workspace(self):
        # Configure layout grids for Sidebar (Col 0) and Workspace content (Col 1)
        self.grid_columnconfigure(0, weight=0) # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1) # Content expansive width
        self.grid_rowconfigure(0, weight=1)
        
        # Create Sidebar Container
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0f172a", border_color="#1e293b", border_width=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        # Sidebar Logo Header
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(25, 20), padx=20, sticky="ew")
        
        logo_lbl = ctk.CTkLabel(logo_frame, text="🔒 SECUREFILE", font=("Segoe UI", 20, "bold"), text_color="#38bdf8")
        logo_lbl.pack(anchor="w")
        
        sub_lbl = ctk.CTkLabel(logo_frame, text="Advanced File Shield", font=("Segoe UI", 10, "bold"), text_color="#64748b")
        sub_lbl.pack(anchor="w", padx=2)
        
        # Navigation Options List
        nav_items = [
            ("Dashboard", "🏠 Dashboard"),
            ("Encrypt File", "🔐 Encrypt File"),
            ("Decrypt File", "🔓 Decrypt File"),
            ("Secure Files", "📁 Secure Files"),
            ("Activity Logs", "📊 Activity Logs"),
            ("Settings", "⚙️ Settings"),
            ("About", "ℹ️ About")
        ]
        
        # Instantiate Navigation Buttons
        btn_start_row = 1
        for idx, (page_name, btn_text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=btn_text,
                height=40,
                corner_radius=6,
                fg_color="transparent",
                text_color="#94a3b8",
                hover_color="#1e293b",
                font=("Segoe UI", 12, "bold"),
                anchor="w",
                command=lambda name=page_name: self.show_page(name)
            )
            btn.grid(row=btn_start_row + idx, column=0, padx=15, pady=4, sticky="ew")
            self.sidebar_buttons[page_name] = btn
            
        # Add Logout Button at bottom
        self.sidebar.grid_rowconfigure(btn_start_row + len(nav_items), weight=1) # Spacer row
        
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout Account",
            height=40,
            corner_radius=6,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#ffffff",
            font=("Segoe UI", 12, "bold"),
            command=self.handle_logout
        )
        logout_btn.grid(row=btn_start_row + len(nav_items) + 1, column=0, padx=15, pady=25, sticky="ew")
        
        # Create Content Canvas Workspace Frame
        self.content_frame = ctk.CTkFrame(self, fg_color="#0f172a")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Load Dashboard initially
        self.show_page("Dashboard")
        
    def show_page(self, page_name):
        # 1. Clean previous content page
        if self.current_page_frame:
            self.current_page_frame.destroy()
            
        # 2. Manage navigation active color states
        for name, btn in self.sidebar_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#1e293b", text_color="#38bdf8")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")
                
        # 3. Instantiate and place page class
        if page_name == "Dashboard":
            self.current_page_frame = DashboardFrame(self.content_frame, self.current_user)
        elif page_name == "Encrypt File":
            self.current_page_frame = EncryptFrame(self.content_frame, self.current_user)
        elif page_name == "Decrypt File":
            self.current_page_frame = DecryptFrame(self.content_frame, self.current_user)
        elif page_name == "Secure Files":
            self.current_page_frame = FileManagerFrame(self.content_frame, self.current_user)
        elif page_name == "Activity Logs":
            self.current_page_frame = LogsFrame(self.content_frame, self.current_user)
        elif page_name == "Settings":
            # Pass appearance theme updater callback to settings frame
            self.current_page_frame = SettingsFrame(self.content_frame, self.current_user, self.on_theme_changed)
        elif page_name == "About":
            self.current_page_frame = AboutFrame(self.content_frame, self.current_user)
            
        self.current_page_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_theme_changed(self, new_theme):
        # Reload Sidebar and Content backgrounds to fit theme dynamically
        self.sidebar.configure(
            fg_color="#0f172a" if new_theme == "Dark" else "#f1f5f9",
            border_color="#1e293b" if new_theme == "Dark" else "#cbd5e1"
        )
        self.content_frame.configure(fg_color="#0f172a" if new_theme == "Dark" else "#cbd5e1")
        # Reload current page to draw with new colors
        for name, btn in self.sidebar_buttons.items():
            if btn.cget("fg_color") != "transparent":
                self.show_page(name)
                break
                
    def handle_logout(self):
        self.current_user = None
        self.sidebar_buttons = {}
        self.current_page_frame = None
        self.show_login_screen()

if __name__ == "__main__":
    app = SecureFileApp()
    app.mainloop()
