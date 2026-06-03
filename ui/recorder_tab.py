import tkinter as tk
from tkinter import ttk, messagebox
import threading
import asyncio
import json
import os
from core.browser_manager import ChromeManager
from core.click_recorder import UniversalRecorderAgent

class RecorderTab(ttk.Frame):
    def __init__(self, parent, file_path="selectors.json"):
        super().__init__(parent)
        self.file_path = file_path
        self.recorder_agent = None
        self.captured_steps_working_list = []
        self.build_universal_recorder_layout()

    def build_universal_recorder_layout(self):
        # Top Panel: Address input fields
        top_frame = ttk.LabelFrame(self, text=" ⚙️ Target Portal Profile Setup ", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Universal Entry Point URL:").pack(side="left", padx=5)
        self.url_entry = ttk.Entry(top_frame, font=("Arial", 11))
        self.url_entry.insert(0, "https://www.goethe.de/ins/in/en/spr/prf/gzb2.cfm")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.rec_btn = ttk.Button(top_frame, text="🔴 START RECORDING", command=self.toggle_recording_session)
        self.rec_btn.pack(side="right", padx=5)

        # Bottom Panel: Dynamic workflow visual spreadsheet matrix
        self.list_frame = ttk.LabelFrame(self, text=" 📋 Sequence Workflow Steps List (Dynamic Size) ", padding=10)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollable container mapping for tracking steps rows layout updates
        self.canvas = tk.Canvas(self.list_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.steps_scroll_window = ttk.Frame(self.canvas)

        self.steps_scroll_window.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.steps_scroll_window, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Persistent Footer Layout Bar
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(footer, text="💾 SAVE CONFIGURED WORKFLOW MACRO", command=self.commit_workflow_to_json).pack(side="right", ipady=5, ipadx=10)

    def toggle_recording_session(self):
        if self.recorder_agent and self.recorder_agent.is_recording:
            # Stop sequence execution command block
            self.recorder_agent.is_recording = False
            self.rec_btn.config(text="🔴 START RECORDING", style="TButton")
            return

        if not ChromeManager.launch_debug_chrome():
            messagebox.showerror("System Error", "Failed to interface or spawn debug Chrome channel.")
            return

        self.rec_btn.config(text="⏹️ STOP & COMPREHEND RECORDING")
        
        # Clear previous elements canvas configurations listings rows
        for widget in self.steps_scroll_window.winfo_children():
            widget.destroy()
            
        self.captured_steps_working_list = []
        self.recorder_agent = UniversalRecorderAgent()
        
        threading.Thread(target=self.run_recorder_thread, args=(self.url_entry.get(),), daemon=True).start()

    def run_recorder_thread(self, url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            steps, err = loop.run_until_complete(
                self.recorder_agent.start_session(url, self.live_append_step_row_callback)
            )
            if steps:
                self.captured_steps_working_list = steps
                self.after(0, lambda: messagebox.showinfo("Macro Verified", f"Recording halted successfully! Process captured {len(steps)} steps metrics rows profiles maps."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def live_append_step_row_callback(self, current_count, step_display_label):
        """Pushes rows into the view configuration canvas instantly on user left-click events"""
        self.after(0, self._render_step_row_ui, current_count, step_display_label)

    def _render_step_row_ui(self, index, display_text):
        row_frame = ttk.Frame(self.steps_scroll_window, padding=4)
        row_frame.pack(fill="x", expand=True, anchor="w", pady=2)

        ttk.Label(row_frame, text=f"Step #{index}:", font=("Arial", 10, "bold"), width=10).pack(side="left")
        
        # Display human-friendly label matching element properties string metrics
        clean_text = display_text if display_text else "Non-Text Action Link Object Element Node"
        lbl = ttk.Label(row_frame, text=f"Clicked on ➔ [{clean_text[:45]}]", width=55, anchor="w")
        lbl.pack(side="left", padx=5)

        # THE REQUIREMENT: Variable layout switch checkbox configuration enabling variable flow logic checkpoints
        chk_var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(row_frame, text="Pause here for User Input / Action Takeover", variable=chk_var)
        chk.pack(side="right", padx=10)

        # Cache reference structures maps arrays
        self.captured_steps_working_list.append({
            "step_index_hook": index - 1,
            "checkbox_variable_reference": chk_var
        })

    def commit_workflow_to_json(self):
        if not self.captured_steps_working_list:
            messagebox.showwarning("Empty Sequence", "No layout parameter steps have been logged. Hit record first.")
            return

        final_steps_payload = []
        # Combine layout steps configurations with checkbox status choices
        for idx, step_meta in enumerate(self.recorder_agent.recorded_steps):
            # Read variables tracking checklist values
            user_input_choice = False
            for ui_map in self.captured_steps_working_list:
                if ui_map.get("step_index_hook") == idx:
                    user_input_choice = ui_map["checkbox_variable_reference"].get()
                    break

            step_meta["manual_input_needed"] = user_input_choice
            step_meta["step_number"] = idx + 1
            final_steps_payload.append(step_meta)

        workflow_data = {
            "workflow_name": "Universal Modular Automation Profile Mapping",
            "target_url": self.url_entry.get(),
            "steps": final_steps_payload
        }

        with open(self.file_path, "w") as f:
            json.dump(workflow_data, f, indent=2)

        messagebox.showinfo("Success", "✅ Universal workflow path compiled and written to selectors.json code-free!")