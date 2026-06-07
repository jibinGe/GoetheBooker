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
        self.log("INIT", "Connecting backend pipeline to your active personal Chrome space...")
        
        async with async_playwright() as p:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://127.0.0.1:9222/json/version")
                    browser_metadata = response.json()
                
                global_ws_url = browser_metadata["webSocketDebuggerUrl"]
                self.log("INIT", "🎯 Connected to Chrome! Initializing State-Verified tracking engine...")
                
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
            self.log("NAVIGATION", f"Loading initial exam page framework: {target_url[:80]}...")
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            macro_steps = self.sel.get("steps", [])
            if not macro_steps:
                self.log("CRITICAL", "❌ No automation steps found in your selectors.json!")
                return

            # --- STAGE 1: GATEWAY SELECT MODULES BUTTON DETECTION ---
            trigger_step = macro_steps[0]
            trigger_selector = trigger_step.get("selector")
            self.log("MONITORING", "⏳ Watching page layout components for the [SELECT MODULES] trigger button...")

            attempt = 1
            while self.is_running:
                if await page.locator(trigger_selector).first.is_visible():
                    self.log("SUCCESS", "🚨 ALERT! Gateway trigger element spotted live on screen!")
                    break
                self.log("STATUS", f"[Check #{attempt}] Gateway closed. Reloading layout state...")
                await page.reload(wait_until="domcontentloaded")
                await page.wait_for_timeout(1000)
                attempt += 1

            if not self.is_running:
                return

            # --- STAGE 2: STRICT STATE-VERIFIED MACRO RUNNER ---
            self.log("CHECKOUT", "⚡ Starting state-verified checkout sequence automation...")

            # Track the steps sequentially to know what comes next
            for idx, step in enumerate(macro_steps):
                if not self.is_running:
                    return

                step_num = step.get("step_number")
                selector = step.get("selector")
                visible_text = step.get("visible_text", "")
                action_type = step.get("action_type", "click")
                current_marker = step.get("page_identity_marker")
                manual_wait = step.get("manual_input_needed", False)

                # Peek ahead to see what the destination page marker should be
                next_marker = None
                if idx + 1 < len(macro_steps):
                    next_marker = macro_steps[idx + 1].get("page_identity_marker")

                self.log("MONITORING", f"📍 [Step #{step_num}] Target Node: [{visible_text or selector}]")

                try:
                    # Pre-check current position validation
                    if current_marker:
                        try:
                            # Only wait if the element isn't already handled/hidden
                            if await page.locator(current_marker).first.is_visible():
                                await page.locator(current_marker).first.wait_for(state="visible", timeout=1000)
                        except TimeoutError:
                            pass

                    element = page.locator(selector).first
                    await element.wait_for(state="visible", timeout=10000)
                    await element.scroll_into_view_if_needed()
                    
                    if action_type == "click":
                        click_confirmed = False
                        
                        for click_attempt in range(1, 6):
                            await element.click(force=True)
                            await page.wait_for_timeout(350) # Give framework a moment to process event
                            
                            # 🛠️ THE SMOOTH STATE FIX:
                            # Only enforce strict look-ahead verification if the NEXT marker is different 
                            # from the current one (meaning we expect a true page/modal transition).
                            if next_marker and next_marker != current_marker:
                                if await page.locator(next_marker).first.is_visible() or await page.locator(next_marker).first.count() > 0:
                                    self.log("STATUS", f"✅ State transitioned safely on attempt #{click_attempt}.")
                                    click_confirmed = True
                                    break
                            else:
                                # For elements like Cookie Banners, Checkboxes, or non-transition steps,
                                # a successful native click execution is all we need to move fast!
                                self.log("STATUS", f"✅ Action executed cleanly on node step #{step_num}")
                                click_confirmed = True
                                break
                            
                            self.log("WARNING", f"⚠️ Click absorbed by framework layout. Re-triggering pointer... ({click_attempt}/5)")
                        
                        if not click_confirmed:
                            await element.click(force=True)

                    elif action_type == "fill":
                        if "username" in selector or "email" in selector.lower():
                            await element.fill(self.config['email'])
                            self.log("STATUS", f"📝 Automatically filled Email Address.")
                        elif "password" in selector.lower():
                            await element.fill(self.config['password'])
                            self.log("STATUS", f"📝 Automatically filled Password.")

                    # Lightning fast traversal safety gap
                    await page.wait_for_timeout(350)

                except TimeoutError:
                    self.log("WARNING", f"⚠️ Step #{step_num} visual anchor bypassed, proceeding down sequence flow...")
                except Exception as step_err:
                    self.log("CRITICAL", f"❌ Step #{step_num} execution barrier fault: {str(step_err)}")

                # Handoff takeover checkpoint
                if manual_wait:
                    self.log("HANDOVER", f"🎉 Step #{step_num} reached perfectly! Pausing bot for your immediate manual payment takeover...")
                    for _ in range(8):
                        print("\a")
                        await asyncio.sleep(0.1)
                    while self.is_running and manual_wait:
                        await asyncio.sleep(1)