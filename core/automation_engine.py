import json
import os
import asyncio
import httpx
from playwright.async_api import async_playwright, TimeoutError

class GoetheDynamicEngine:
    def __init__(self, config, log_callback, selectors_file="selectors.json"):
        self.config = config
        self.log = log_callback
        self.is_running = True
        
        with open(selectors_file, "r") as f:
            self.sel = json.load(f)

    async def run_pipeline(self):
        async with async_playwright() as p:
            self.log("INIT", "Querying global browser debugger endpoints via DevTools API...")
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://127.0.0.1:9222/json/version")
                    browser_metadata = response.json()
                
                global_ws_url = browser_metadata["webSocketDebuggerUrl"]
                self.log("INIT", "🎯 Global browser link spotted! Attaching pipeline channel...")
                
                browser = await p.chromium.connect_over_cdp(global_ws_url)
                
                if browser.contexts:
                    browser_context = browser.contexts[0]
                    page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
                else:
                    browser_context = await browser.new_context()
                    page = await browser_context.new_page()
                    
            except Exception as e:
                self.log("CRITICAL", f"Failed attachment profile link: {str(e)}")
                return

            target_url = self.sel.get("target_url", self.config['url'])
            self.log("NAVIGATION", f"Directing target tab instance to: {target_url}...")
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            macro_steps = self.sel.get("steps", [])
            self.log("MONITORING", f"Loaded macro sequence containing {len(macro_steps)} actions.")

            for step in macro_steps:
                if not self.is_running:
                    return

                step_num = step.get("step_number")
                selector = step.get("selector")
                visible_text = step.get("visible_text", "")
                action_type = step.get("action_type", "click")
                manual_wait = step.get("manual_input_needed", False)

                self.log("MONITORING", f"[Step #{step_num}] Interacting with [{visible_text or selector}]...")

                try:
                    # 🛠️ MODAL STABILIZATION FIX: 
                    # Use locator.first and wait explicitly for actionable states (visible + attached)
                    element = page.locator(selector).first
                    
                    # Increase timeout to 15s specifically for dynamic elements inside modals
                    await element.wait_for(state="visible", timeout=15000)
                    await element.wait_for(state="attached", timeout=15000)
                    
                    # Force scroll element into the viewable viewport bounding box to bypass modal clipping
                    await element.scroll_into_view_if_needed()
                    
                    if action_type == "click":
                        # Use force=True to bypass any transparent loading spinners block overlays
                        await element.click(force=True)
                        self.log("STATUS", f"✅ Successfully executed step #{step_num}")
                    
                    # Dynamic buffer loop to allow modal animations to complete rendering
                    await page.wait_for_timeout(1000)

                except TimeoutError:
                    self.log("WARNING", f"⚠️ Step #{step_num} target missing or hidden inside modal layout wrapper. Skipping...")
                except Exception as step_err:
                    self.log("CRITICAL", f"❌ Step #{step_num} runtime failure: {str(step_err)}")

                # 🛑 MANUAL INPUT OVERLAY FORWARDER
                if manual_wait:
                    self.log("HANDOVER", f"⏸️ Step #{step_num} requested manual intervention check. Pausing engine automation...")
                    while self.is_running and manual_wait:
                        await asyncio.sleep(1)
                    self.log("MONITORING", "▶️ Handover clear. Resuming background engine sequence execution...")

            self.log("HANDOVER", "🛑 Entire sequential macro path fully replayed.")
            while self.is_running:
                await asyncio.sleep(1)