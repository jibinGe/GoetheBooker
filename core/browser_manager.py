import os
import sys
import subprocess
import platform
import time
import httpx

class ChromeManager:
    @staticmethod
    def get_chrome_path():
        """Detects host operating system and returns native Chrome path profiles."""
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif os_type == "Windows":  # Windows
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        return None

    @classmethod
    def launch_debug_chrome(cls, port=9222):
        """Spawns a clean, multi-profile compatible debugging instance of Chrome in Incognito mode."""
        chrome_path = cls.get_chrome_path()
        if not chrome_path or not os.path.exists(chrome_path):
            print(f" (SYSTEM ERROR) -> Native Google Chrome installation missing.")
            return False

        # 1. Quick check to see if an instance is already listening on this exact port
        try:
            with httpx.Client() as client:
                res = client.get(f"http://127.0.0.1:{port}/json/version", timeout=1.0)
                if res.status_code == 200:
                    print(f" (SYSTEM) -> Chrome debug engine already active on port {port}. Attaching...")
                    return True
        except Exception:
            pass

        print(f" (SYSTEM) -> Deploying isolated Incognito Chrome instance on port {port}...")
        
        # 2. Dynamic profiles paths separation
        automation_data_dir = os.path.join(os.getcwd(), "chrome_debug_profile")
        target_profile_directory = "Profile 2"  # Keep this assigned to point to your target environment profile
        
        os_type = platform.system()
        flags = [
            chrome_path, 
            f"--remote-debugging-port={port}", 
            f"--remote-debugging-address=127.0.0.1",
            f"--user-data-dir={automation_data_dir}", 
            f"--profile-directory={target_profile_directory}",
            "--incognito",                     # 🛠️ THE FIX: Forces the window directly into an Incognito sandbox session
            "--no-first-run",
            "--no-default-browser-check"
        ]
        
        if os_type == "Windows":
            subprocess.Popen(flags, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            # On macOS, using the unique user-data-dir combined with --incognito spins up a completely unlinked engine context cleanly
            subprocess.Popen(flags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            
        time.sleep(5.0) # Buffer safety window to allow the private browser instance to mount the local port interface securely
        return True