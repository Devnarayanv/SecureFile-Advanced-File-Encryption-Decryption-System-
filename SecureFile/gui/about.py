import sys
import customtkinter as ctk
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

class AboutFrame(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#0f172a")
        self.username = username
        self.init_ui()
        
    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid_columnconfigure(0, weight=1)
        
        # Logo Emoji
        shield = ctk.CTkLabel(scroll, text="🛡️", font=("Segoe UI Emoji", 56))
        shield.pack(pady=(20, 5))
        
        # Title Banner
        title_lbl = ctk.CTkLabel(scroll, text="SECUREFILE", font=("Segoe UI", 26, "bold"), text_color="#38bdf8")
        title_lbl.pack(pady=2)
        
        subtitle_lbl = ctk.CTkLabel(scroll, text="Advanced File Encryption & Decryption System", font=("Segoe UI", 13, "bold"), text_color="#94a3b8")
        subtitle_lbl.pack(pady=(0, 20))
        
        intro_text = (
            "SecureFile is a desktop security utility designed for college Operating Systems curricula. "
            "It provides real-time authenticated file encryption and decryption tools combined with dynamic process telemetry "
            "and resource diagnostics."
        )
        intro_lbl = ctk.CTkLabel(scroll, text=intro_text, font=("Segoe UI", 12), text_color="#cbd5e1", wraplength=550, justify="center")
        intro_lbl.pack(pady=10)
        
        # =====================================================================
        # CARD 1: TECH STACK
        # =====================================================================
        tech_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        tech_card.pack(fill="x", padx=20, pady=10)
        
        tech_title = ctk.CTkLabel(tech_card, text="⚙️ Project Technology Stack", font=("Segoe UI", 13, "bold"), text_color="#38bdf8", anchor="w")
        tech_title.pack(fill="x", padx=15, pady=(12, 5))
        
        tech_items = (
            "• Python 3    – Core logic script and multi-threaded orchestration\n"
            "• CustomTkinter – High-fidelity desktop GUI wrapper and dynamic visual canvas\n"
            "• Cryptography – Authenticated AES-256 GCM encryption and PBKDF2 SHA-256 KDF key generation\n"
            "• SQLite 3    – Relational historical file database and configuration properties\n"
            "• PSUtil      – Direct OS API binder to poll CPU cycles, memory, and process handles"
        )
        tech_lbl = ctk.CTkLabel(tech_card, text=tech_items, font=("Segoe UI", 12), text_color="#cbd5e1", justify="left", anchor="w")
        tech_lbl.pack(fill="x", padx=15, pady=(0, 15))
        
        # =====================================================================
        # CARD 2: OS CONCEPTS
        # =====================================================================
        os_card = ctk.CTkFrame(scroll, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        os_card.pack(fill="x", padx=20, pady=10)
        
        os_title = ctk.CTkLabel(os_card, text="💻 Demonstrated Operating System Concepts", font=("Segoe UI", 13, "bold"), text_color="#38bdf8", anchor="w")
        os_title.pack(fill="x", padx=15, pady=(12, 5))
        
        concepts = [
            ("A. File Management", 
             "Direct OS file creation, deletion, stream writing, and metadata inquiries. Reads and displays file permissions "
             "using octal bitmask conversions and restores system file modes during data recovery."),
            
            ("B. Process & Thread Management", 
             "Orchestrates a dedicated thread pool to run background workers. Decouples expensive cryptographic workloads "
             "from the main GUI process thread, preventing window locking, and displays live worker status and active thread IDs."),
            
            ("C. Storage Management", 
             "Leverages filesystem indicators to compute total protected size. Queries OS drive capacities using sector-level "
             "information to prevent disk exhaustion before executing large encryption streams."),
            
            ("D. Resource Diagnostics & Telemetry", 
             "Polls active resource handlers, memory Resident Set Size (RSS), and thread loops using OS processes APIs. "
             "Implements context handlers to prevent leakage of file handles or kernel handles."),
             
            ("E. Security & Authentication Access", 
             "Implements hashing for access control via salt derivations and brute force lockout timers stored in SQLite "
             "to enforce rate-limiting across system reboots.")
        ]
        
        for subtitle, desc in concepts:
            item_frame = ctk.CTkFrame(os_card, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=5)
            
            sub_lbl = ctk.CTkLabel(item_frame, text=subtitle, font=("Segoe UI", 12, "bold"), text_color="#10b981", anchor="w")
            sub_lbl.pack(fill="x", pady=(2, 1))
            
            desc_lbl = ctk.CTkLabel(item_frame, text=desc, font=("Segoe UI", 11), text_color="#cbd5e1", wraplength=520, justify="left", anchor="w")
            desc_lbl.pack(fill="x", pady=(0, 2))
            
        # Spacing padding
        ctk.CTkLabel(os_card, text="", height=5, fg_color="transparent").pack()
        
        # Footer
        footer_lbl = ctk.CTkLabel(scroll, text="SecureFile System v1.0.0 | Academic OS Project", font=("Segoe UI", 10), text_color="#64748b")
        footer_lbl.pack(pady=20)
