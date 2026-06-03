import os
import json
import tkinter as tk
from tkinter import ttk
from ui.dashboard import OperationsTab
from ui.recorder_tab import RecorderTab

SELECTORS_FILE = "selectors.json"

# Fallback setup dictionary profiles parameters
FALLBACK_MAP = {
  "cookies": { "accept_banner_btn": "button:has-text('Accept All')" },
  "landing_page": { "error_text_trigger": "text=Sorry, our dates cannot be displayed temporarily", "card_price_anchor": "INR" },
  "module_selection": { "select_modules_btn": "button:has-text('SELECT MODULES')", "continue_btn": "button:has-text('CONTINUE')", "fully_booked_text": "Fully booked" },
  "auth_page": { "book_for_myself_btn": "button:has-text('BOOK FOR MYSELF')", "email_input": "input[type='email']", "password_input": "input[type='password']", "login_submit_btn": "button:has-text('LOG IN')" }
}

def bootstrap_application():
    if not os.path.exists(SELECTORS_FILE):
        with open(SELECTORS_FILE, "w") as f:
            json.dump(FALLBACK_MAP, f, indent=2)

    root = tk.Tk()
    root.title("GoetheBooker Enterprise Distribution Client (MVC Engine)")
    root.geometry("960x670")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    tab_ops = OperationsTab(notebook)
    tab_rec = RecorderTab(notebook)
    
    notebook.add(tab_ops, text=" Live Operations Workspace Dashboard ")
    notebook.add(tab_rec, text=" 🔴 Automated Visual Elements Recorder Module ")
    
    root.mainloop()

if __name__ == "__main__":
    bootstrap_application()