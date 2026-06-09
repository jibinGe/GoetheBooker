import json
import os
import sys
import asyncio
import httpx
from playwright.async_api import async_playwright, TimeoutError

class GoetheDynamicEngine:
    def __init__(self, config, log_callback, selectors_file="selectors.json"):
        """
        Initializes the high-speed state-verified booking engine.
        :param config: Dictionary containing 'email', 'password', 'url', etc.
        :param log_callback: Function reference for terminal UI logging pipeline.
        :param selectors_file: Path to the structural tracking JSON configuration.
        """
        self.config = config
        self.log = log_callback
        self.is_running = True
        self.selectors_file = selectors_file
        self.steps = []
        
        self._load_workflow()

    def _load_workflow(self):
        """Parses the operational pipeline tracking step profiles."""
        try:
            if os.path.exists(self.selectors_file):
                with open(self.selectors_file, "r") as f:
                    workflow_data = json.load(f)
                    self.steps = workflow_data.get("steps", [])
                self.log("INIT", f"Loaded {len(self.steps)} structural steps from {self.selectors_file}")
            else:
                self.log("CRITICAL", f"Target file '{self.selectors_file}' not found.")
        except Exception as e:
            self.log("CRITICAL", f"Failed to parse workflow configuration: {str(e)}")

    async def run_pipeline(self):
        self.log("INIT", "Connecting backend pipeline to your active personal Chrome space...")
        
        async with async_playwright() as p:
            # --- STAGE 1: CONNECT TO RUNNING CHROME INSTANCE ---
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://127.0.0.1:9222/json/version")
                    browser_metadata = response.json()
                
                global_ws_url = browser_metadata["webSocketDebuggerUrl"]
                browser = await p.chromium.connect_over_cdp(global_ws_url)
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else await context.new_page()
            except Exception as e:
                self.log("CRITICAL", f"Connection interface breakdown to port 9222: {str(e)}")
                return

            self.log("READY", f"Orchestrator online. Launching target entry: {self.config.get('url')}")
            
            # --- STAGE 2: NAVIGATION BOUNDARY SYNC ---
            try:
                await page.goto(self.config.get("url"), wait_until="commit")
                await page.wait_for_load_state("domcontentloaded")
            except Exception as e:
                self.log("WARNING", f"Initial page redirection delayed, processing layout verification: {str(e)}")

            # --- STAGE 3: PIPELINE EXECUTION ENGINE LOOP ---
            for step in self.steps:
                if not self.is_running:
                    self.log("STATUS", "Aborting sequence loop execution manually.")
                    break
                
                step_num = step.get("step_number", "?")
                action = step.get("action_type", "click").lower()
                selector = step.get("selector")
                identity_marker = step.get("page_identity_marker")
                visible_text = step.get("visible_text", "")
                manual_wait = step.get("manual_input_needed", False)

                self.log("STAGE", f"▶️ Commencing Step #{step_num} [{action.upper()}] -> '{visible_text}'")

                try:
                    # --- CHECK 1: PRE-FLIGHT BOUNDARY SYNCHRONIZATION ---
                    if identity_marker:
                        self.log("VERIFY", f"⏳ Synchronizing context layout with anchor: `{identity_marker}`...")
                        try:
                            locator = page.locator(identity_marker).first
                            # Upgraded strategy: dynamically track layout appearance safely with higher timeout
                            await locator.wait_for(state="visible", timeout=12000)
                        except TimeoutError:
                            self.log("WARNING", f"⚠️ Structural anchor `{identity_marker}` not visible instantly. Searching direct selector trees...")

                    # --- CHECK 2: TARGET AVAILABILITY CHECK ---
                    target_element = page.locator(selector).first
                    try:
                        # Ensure object target is fully visible, rendered, and ready to accept input actions
                        await target_element.wait_for(state="visible", timeout=10000)
                    except TimeoutError:
                        self.log("CRITICAL", f"❌ Target element selector failed visibility check: `{selector}`. Step dropped.")
                        continue

                    # Cache layout fingerprint before sending mutation triggers
                    url_before = page.url

                    # --- INTERACTION DESPATCH LAYER ---
                    if action == "click":
                        await target_element.scroll_into_view_if_needed()
                        try:
                            await target_element.click(timeout=3000)
                            self.log("ACTION", f"🎯 Dispatched native physical click signal to target element.")
                        except TimeoutError:
                            self.log("WARNING", "⚠️ Pointer action obstructed. Deploying layout force-override...")
                            await target_element.click(force=True, timeout=3000)
                            self.log("ACTION", f"⚡ Forced programmatic click override successfully.")
                        
                    elif action == "fill":
                        await target_element.scroll_into_view_if_needed()
                        await target_element.click(timeout=2000)
                        await target_element.fill("")
                        
                        payload_value = visible_text
                        if "username" in selector or "email" in selector or "login" in selector:
                            payload_value = self.config.get("email", visible_text)
                        elif "password" in selector:
                            payload_value = self.config.get("password", visible_text)
                        
                        await target_element.type(payload_value, delay=40)
                        self.log("ACTION", f"✏️ Input structural values into parameter field successfully.")

                    # --- CHECK 4: PRODUCTION-HARDENED INTER-STEP SETTLING ENGINE ---
                    url_after = page.url
                    if url_before != url_after:
                        self.log("STATE_CHANGE", f"🌐 Navigation transition observed! URL shifted to: {url_after}")
                        self.log("VERIFY", "⏳ Balancing asynchronous backend rendering state...")
                        try:
                            await page.wait_for_load_state("networkidle", timeout=4000)
                        except TimeoutError:
                            pass
                    else:
                        # FIX: For single-page DOM transitions (like Step #2 clicking and opening checkboxes),
                        # we must stall processing until the active networking operations have reached an absolute rest state.
                        self.log("VERIFY", "⏳ Balancing dynamic frame backend threads (SPA mutation)...")
                        try:
                            # Forces Playwright to analyze the active background network stream and wait until zero requests are pending.
                            await page.wait_for_load_state("networkidle", timeout=3500)
                        except TimeoutError:
                            # If the application uses persistent polling/websockets, catch the timeout and breathe naturally
                            await asyncio.sleep(1.0)

                    # Final microsecond layout settling pad
                    await asyncio.sleep(0.5)

                except Exception as step_err:
                    self.log("CRITICAL", f"❌ Step #{step_num} execution barrier fault: {str(step_err)}")

                # --- STAGE 4: MANUAL TAKEOVER CONSOLE HANDOFF ---
                if manual_wait:
                    self.log("HANDOVER", f"🎉 Step #{step_num} reached perfectly! Pausing engine context...")
                    for _ in range(8):
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                        await asyncio.sleep(0.1)
                    
                    while self.is_running and manual_wait:
                        await asyncio.sleep(1)

            self.log("HANDOVER", "🛑 Operational loop cycle successfully finished.")
            while self.is_running:
                await asyncio.sleep(1)