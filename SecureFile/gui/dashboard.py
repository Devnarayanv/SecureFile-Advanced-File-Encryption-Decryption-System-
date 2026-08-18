import sys
import customtkinter as ctk
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from database import database
from utils.system_monitor import get_system_stats
from utils.file_utils import format_size

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, username):
        super().__init__(parent, fg_color="#0f172a") # Slate 900
        self.username = username
        self.init_ui()
        self.update_telemetry()
        
    def init_ui(self):
        # Configure layout grids
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1) # Let the log table expand
        
        # 1. Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        
        welcome_lbl = ctk.CTkLabel(header, text=f"Welcome, {self.username.capitalize()}", font=("Segoe UI", 24, "bold"), text_color="#f8fafc")
        welcome_lbl.pack(side="left")
        
        status_badges_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_badges_frame.pack(side="right")
        
        # Badges
        engine_badge = ctk.CTkLabel(status_badges_frame, text="AES-256 GCM", font=("Segoe UI", 11, "bold"), fg_color="#1e293b", text_color="#38bdf8", corner_radius=6, padx=8, pady=2)
        engine_badge.pack(side="left", padx=5)
        
        sec_badge = ctk.CTkLabel(status_badges_frame, text="SECURE", font=("Segoe UI", 11, "bold"), fg_color="#065f46", text_color="#34d399", corner_radius=6, padx=8, pady=2)
        sec_badge.pack(side="left", padx=5)
        
        db_badge = ctk.CTkLabel(status_badges_frame, text="CONNECTED", font=("Segoe UI", 11, "bold"), fg_color="#065f46", text_color="#34d399", corner_radius=6, padx=8, pady=2)
        db_badge.pack(side="left", padx=5)
        
        # 2. Stats Grid Row
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # We will initialize the stat cards. They will be updated dynamically in update_telemetry.
        self.cards = {}
        self.create_stat_card(0, "🔒 Encrypted", "0", "Total Files Encrypted")
        self.create_stat_card(1, "🔓 Decrypted", "0", "Total Files Decrypted")
        self.create_stat_card(2, "📁 Size Protected", "0 B", "Storage Volume Shielded")
        self.create_stat_card(3, "📊 Success Rate", "100%", "Successful Operations")

        # 3. Main Split Area: Recent Activity (Left) and System Monitor (Right)
        # Left Panel (Recent Activity)
        self.activity_panel = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        self.activity_panel.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)
        self.activity_panel.grid_columnconfigure(0, weight=1)
        self.activity_panel.grid_rowconfigure(1, weight=1)
        
        act_title = ctk.CTkLabel(self.activity_panel, text="Recent System Operations", font=("Segoe UI", 16, "bold"), text_color="#f8fafc", anchor="w")
        act_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        
        # Table container
        self.table_frame = ctk.CTkFrame(self.activity_panel, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Right Panel (System Monitor)
        self.monitor_panel = ctk.CTkFrame(self, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12)
        self.monitor_panel.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.monitor_panel.grid_columnconfigure(0, weight=1)
        
        mon_title = ctk.CTkLabel(self.monitor_panel, text="System Resource Monitor", font=("Segoe UI", 16, "bold"), text_color="#f8fafc", anchor="w")
        mon_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        
        # Monitor details container
        monitor_details = ctk.CTkFrame(self.monitor_panel, fg_color="transparent")
        monitor_details.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        monitor_details.grid_columnconfigure(0, weight=1)
        
        # System widgets (CPU, RAM, Disk)
        self.cpu_lbl = ctk.CTkLabel(monitor_details, text="CPU Usage: 0.0%", font=("Segoe UI", 12), text_color="#94a3b8")
        self.cpu_lbl.grid(row=0, column=0, sticky="w", pady=(5, 2))
        self.cpu_bar = ctk.CTkProgressBar(monitor_details, fg_color="#0f172a", progress_color="#3b82f6")
        self.cpu_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.cpu_bar.set(0)
        
        self.ram_lbl = ctk.CTkLabel(monitor_details, text="RAM Usage: 0.0%", font=("Segoe UI", 12), text_color="#94a3b8")
        self.ram_lbl.grid(row=2, column=0, sticky="w", pady=(5, 2))
        self.ram_bar = ctk.CTkProgressBar(monitor_details, fg_color="#0f172a", progress_color="#10b981")
        self.ram_bar.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.ram_bar.set(0)
        
        self.disk_lbl = ctk.CTkLabel(monitor_details, text="Disk Free Space: N/A", font=("Segoe UI", 12), text_color="#94a3b8")
        self.disk_lbl.grid(row=4, column=0, sticky="w", pady=(5, 2))
        self.disk_bar = ctk.CTkProgressBar(monitor_details, fg_color="#0f172a", progress_color="#8b5cf6")
        self.disk_bar.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        self.disk_bar.set(0)
        
        # Process Widgets (OS Process stats)
        proc_separator = ctk.CTkFrame(monitor_details, height=1, fg_color="#334155")
        proc_separator.grid(row=6, column=0, sticky="ew", pady=10)
        
        proc_title = ctk.CTkLabel(monitor_details, text="Active Process Diagnostics (OS Concepts)", font=("Segoe UI", 13, "bold"), text_color="#38bdf8", anchor="w")
        proc_title.grid(row=7, column=0, sticky="w", pady=(5, 10))
        
        self.proc_cpu_lbl = ctk.CTkLabel(monitor_details, text="• Worker CPU Time: 0.0%", font=("Segoe UI", 12), text_color="#f8fafc", anchor="w")
        self.proc_cpu_lbl.grid(row=8, column=0, sticky="w", pady=2)
        
        self.proc_ram_lbl = ctk.CTkLabel(monitor_details, text="• Working Set RAM: 0 B", font=("Segoe UI", 12), text_color="#f8fafc", anchor="w")
        self.proc_ram_lbl.grid(row=9, column=0, sticky="w", pady=2)
        
        self.proc_threads_lbl = ctk.CTkLabel(monitor_details, text="• Thread Pool Count: 1 Threads", font=("Segoe UI", 12), text_color="#f8fafc", anchor="w")
        self.proc_threads_lbl.grid(row=10, column=0, sticky="w", pady=2)
        
        self.proc_handles_lbl = ctk.CTkLabel(monitor_details, text="• Active OS Handles: 0 Handles", font=("Segoe UI", 12), text_color="#f8fafc", anchor="w")
        self.proc_handles_lbl.grid(row=11, column=0, sticky="w", pady=2)

    def create_stat_card(self, col, icon_title, value, subtitle):
        card = ctk.CTkFrame(self.stats_frame, fg_color="#1e293b", border_color="#334155", border_width=1, corner_radius=12, height=110)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
        card.grid_propagate(False)
        
        # Grid layout inside the card
        card.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(card, text=icon_title, font=("Segoe UI", 12, "bold"), text_color="#3b82f6" if col==0 else "#10b981" if col==1 else "#8b5cf6" if col==2 else "#f59e0b", anchor="w")
        title_lbl.grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")
        
        val_lbl = ctk.CTkLabel(card, text=value, font=("Segoe UI", 24, "bold"), text_color="#f8fafc", anchor="w")
        val_lbl.grid(row=1, column=0, padx=15, pady=0, sticky="w")
        
        sub_lbl = ctk.CTkLabel(card, text=subtitle, font=("Segoe UI", 10), text_color="#64748b", anchor="w")
        sub_lbl.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Save reference
        self.cards[col] = (val_lbl, sub_lbl)

    def update_telemetry(self):
        """
        Periodically updates the dashboard statistics and live system monitoring metrics.
        """
        # Fetch DB metrics
        stats = database.get_stats()
        
        # Update Cards
        self.cards[0][0].configure(text=str(stats["total_encrypted"]))
        self.cards[1][0].configure(text=str(stats["total_decrypted"]))
        self.cards[2][0].configure(text=format_size(stats["total_size"]))
        
        total_ops = stats["success_ops"] + stats["failed_ops"]
        rate = "100%"
        if total_ops > 0:
            rate = f"{(stats['success_ops'] / total_ops) * 100:.1f}%"
        self.cards[3][0].configure(text=rate)
        self.cards[3][1].configure(text=f"Success: {stats['success_ops']} / Fail: {stats['failed_ops']}")
        
        # Update Recent Activity Table
        self.refresh_activity_table()
        
        # Get System telemetry
        telemetry = get_system_stats()
        
        # Update System Widgets
        self.cpu_lbl.configure(text=f"CPU Usage: {telemetry['sys_cpu']}%")
        self.cpu_bar.set(telemetry["sys_cpu"] / 100.0)
        
        self.ram_lbl.configure(text=f"RAM Usage: {telemetry['sys_ram_percent']}% ({telemetry['sys_ram_used']} / {telemetry['sys_ram_total']})")
        self.ram_bar.set(telemetry["sys_ram_percent"] / 100.0)
        
        self.disk_lbl.configure(text=f"Disk Usage: {telemetry['sys_disk_percent']}% ({telemetry['sys_disk_free']} free of {telemetry['sys_disk_total']})")
        self.disk_bar.set(telemetry["sys_disk_percent"] / 100.0)
        
        # Update Process Diagnostics
        self.proc_cpu_lbl.configure(text=f"• Worker CPU Time: {telemetry['proc_cpu']}%")
        self.proc_ram_lbl.configure(text=f"• Working Set RAM: {telemetry['proc_ram']}")
        self.proc_threads_lbl.configure(text=f"• Thread Pool Count: {telemetry['proc_threads']} Threads")
        self.proc_handles_lbl.configure(text=f"• Active OS Handles: {telemetry['proc_handles']} Handles")
        
        # Schedule next update in 2000 milliseconds
        self.after(2000, self.update_telemetry)
        
    def refresh_activity_table(self):
        # Clear old rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        # Headers
        headers = ["Time", "File", "Operation", "Size", "Status"]
        self.table_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        for idx, h in enumerate(headers):
            h_lbl = ctk.CTkLabel(self.table_frame, text=h, font=("Segoe UI", 11, "bold"), text_color="#94a3b8", anchor="w")
            h_lbl.grid(row=0, column=idx, padx=5, pady=5, sticky="ew")
            
        # Fetch last 5 logs
        logs = database.get_activity_logs()[:5]
        
        if not logs:
            no_logs = ctk.CTkLabel(self.table_frame, text="No operations recorded yet.", font=("Segoe UI", 12), text_color="#64748b")
            no_logs.grid(row=1, column=0, columnspan=5, pady=20)
            return
            
        for r_idx, log in enumerate(logs):
            row_num = r_idx + 1
            
            # Format time from YYYY-MM-DD HH:MM:SS
            raw_time = log["timestamp"]
            try:
                # Keep only HH:MM:SS part
                time_str = raw_time.split(" ")[1]
            except Exception:
                time_str = raw_time
                
            filename = log["filename"] if log["filename"] else "-"
            # Limit filename display length
            if len(filename) > 20:
                filename = filename[:17] + "..."
                
            op = log["operation"]
            size_str = format_size(log["original_size"]) if log["original_size"] is not None else "-"
            status = log["result"]
            
            # Alternate row background colors
            row_bg = "#1e293b" if row_num % 2 == 0 else "#16202c"
            
            # Create a row frame to hold labels and get alternating background
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_bg, corner_radius=4)
            row_frame.grid(row=row_num, column=0, columnspan=5, sticky="ew", pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            ctk.CTkLabel(row_frame, text=time_str, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=0, padx=5, pady=4, sticky="ew")
            ctk.CTkLabel(row_frame, text=filename, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=1, padx=5, pady=4, sticky="ew")
            ctk.CTkLabel(row_frame, text=op, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=2, padx=5, pady=4, sticky="ew")
            ctk.CTkLabel(row_frame, text=size_str, font=("Segoe UI", 11), text_color="#cbd5e1", anchor="w").grid(row=0, column=3, padx=5, pady=4, sticky="ew")
            
            # Status Badge color
            badge_color = "#34d399" if status == "SUCCESS" else "#f87171"
            ctk.CTkLabel(row_frame, text=status, font=("Segoe UI", 10, "bold"), text_color=badge_color, anchor="w").grid(row=0, column=4, padx=5, pady=4, sticky="ew")
