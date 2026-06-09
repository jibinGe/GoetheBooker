import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import asyncio
from core.browser_manager import ChromeManager
from core.automation_engine import GoetheDynamicEngine

class OperationsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.engine = None
        self.loop = None
        self.build_tab_layout()

    def build_tab_layout(self):
        lf = ttk.LabelFrame(self, text=" System Runtime Controls Parameter Matrix ", padding=10)
        lf.place(x=10, y=10, width=340, height=610)
        
        ttk.Label(lf, text="Exam Target Center Location:").pack(anchor="w")
        self.loc_ent = ttk.Entry(lf); self.loc_ent.insert(0, "Chennai"); self.loc_ent.pack(fill="x", pady=5)
        
        ttk.Label(lf, text="Delivery Format Profile:").pack(anchor="w")
        self.form_combo = ttk.Combobox(lf, values=["Paper-based", "Computer-based"], state="readonly")
        self.form_combo.set("Paper-based"); self.form_combo.pack(fill="x", pady=5)
        
        ttk.Label(lf, text="Selected Tracking Modules (Comma Split):").pack(anchor="w")
        self.mod_ent = ttk.Entry(lf); self.mod_ent.insert(0, "LISTENING"); self.mod_ent.pack(fill="x", pady=5)
        
        ttk.Label(lf, text="Authentication User Identity (Email):").pack(anchor="w")
        self.email_ent = ttk.Entry(lf); self.email_ent.insert(0, "0001oneteam@gmail.com"); self.email_ent.pack(fill="x", pady=5)
        
        ttk.Label(lf, text="Authentication User Secure Password:").pack(anchor="w")
        self.pass_ent = ttk.Entry(lf, show="*"); self.pass_ent.insert(0, "Oneteam@2026"); self.pass_ent.pack(fill="x", pady=15)
        
        self.start_btn = ttk.Button(lf, text="⚡ LAUNCH ENGINE AUTOMATION", command=self.start_bot_worker)
        self.start_btn.pack(fill="x", ipady=5, pady=5)
        
        self.stop_btn = ttk.Button(lf, text="🛑 FORCE CRASH ENGINE PIPELINE", state="disabled", command=self.stop_bot_worker)
        self.stop_btn.pack(fill="x", ipady=3)

        rt = ttk.LabelFrame(self, text=" Real-Time Activity Log Output Terminal Panel ", padding=10)
        rt.place(x=370, y=10, width=540, height=610)
        self.txt = scrolledtext.ScrolledText(rt, bg="#111111", fg="#39ff14", font=("Courier", 11))
        self.txt.pack(fill="both", expand=True)

    def log(self, step, msg):
        self.after(0, lambda: self.txt.insert(tk.END, f"[{step.upper()}] -> {msg}\n"))
        self.after(0, lambda: self.txt.see(tk.END))

    def start_bot_worker(self):
        # Automatically launch Chrome using our OS-independent browser core script first
        if not ChromeManager.launch_debug_chrome():
            self.log("ERROR", "Automatic Chrome deployment crashed. Open Chrome manually on port 9222.")
            return

        config = {
            "url": "https://www.goethe.de/ins/in/en/spr/prf/gzb2.cfm?examId=5C5C9BDA81DFFB818AD901922CC35F512BD0DD7FEAC4F9B50BFF07AA85CB98AAD9CEEDCDDF1F7F4788E6FE8650DF4282E8FA8B9256815ECCA72FD645C4D79FEC",
            "location": self.loc_ent.get(),
            "format": self.form_combo.get(),
            "modules": [m.strip() for m in self.mod_ent.get().split(",") if m.strip()],
            "email": self.email_ent.get(),
            "password": self.pass_ent.get()
        }
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.async_worker_entry, args=(config,), daemon=True).start()

    def async_worker_entry(self, config):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.engine = GoetheDynamicEngine(config, self.log)
        try: self.loop.run_until_complete(self.engine.run_pipeline())
        except Exception as e: self.log("CRITICAL", str(e))
        finally: self.reset_ui()

    def stop_bot_worker(self):
        if self.engine: self.engine.is_running = False
        if self.loop: self.loop.call_soon_threadsafe(self.loop.stop)

    def reset_ui(self):
        self.after(0, lambda: self.start_btn.config(state="normal"))
        self.after(0, lambda: self.stop_btn.config(state="disabled"))