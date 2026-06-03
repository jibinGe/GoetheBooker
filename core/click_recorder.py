import asyncio
import httpx
from playwright.async_api import async_playwright

class UniversalRecorderAgent:
    def __init__(self):
        self.recorded_steps = []
        self.is_recording = True

    async def start_session(self, target_url, step_logged_callback):
        async with async_playwright() as p:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://127.0.0.1:9222/json/version")
                    global_ws_url = response.json()["webSocketDebuggerUrl"]
                
                browser = await p.chromium.connect_over_cdp(global_ws_url)
                browser_context = browser.contexts[0]
                page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
            except Exception as e:
                return None, f"Failed connection hook: {str(e)}"

            self.recorded_steps = []

            # Clean JavaScript Tracker Injection Definition
            async def inject_mouse_listeners():
                try:
                    await page.evaluate("""() => {
                        // Prevent duplicating tracking boundaries if already active
                        if (window.UniversalTrackerAttached) return;
                        window.UniversalTrackerAttached = true;

                        document.body.style.cursor = 'crosshair';
                        
                        let box = document.createElement('div');
                        box.style.position = 'absolute'; box.style.border = '2px dashed #00ff00';
                        box.style.background = 'rgba(0, 255, 0, 0.05)'; box.style.pointerEvents = 'none';
                        box.style.zIndex = '999999'; document.body.appendChild(box);

                        document.addEventListener('mouseover', (e) => {
                            let r = e.target.getBoundingClientRect();
                            box.style.top = (r.top + window.scrollY) + 'px';
                            box.style.left = (r.left + window.scrollX) + 'px';
                            box.style.width = r.width + 'px'; box.style.height = r.height + 'px';
                        }, true);

                        document.addEventListener('click', (e) => {
                            let path = '';
                            if (e.target.id) { path = '#' + e.target.id; }
                            else if (e.target.innerText && e.target.innerText.trim().length > 0) {
                                path = e.target.tagName.toLowerCase() + ":has-text('" + e.target.innerText.trim().split('\\n')[0].replace(/'/g, "\\\\'") + "')";
                            } else {
                                path = e.target.tagName.toLowerCase();
                                if (e.target.className) path += '.' + [...e.target.classList].join('.');
                            }
                            
                            window.registerUniversalClickToPython(path, e.target.innerText ? e.target.innerText.trim().split('\\n')[0] : '', e.target.tagName);
                        }, true);
                    }""")
                except Exception:
                    pass # Ignore temporary evaluation drops during frame shifts

            def capture_hook(selector, text, tag):
                if not self.is_recording:
                    return
                
                # Check for and ignore accidental or rapid double-click step duplications
                if self.recorded_steps and self.recorded_steps[-1]["selector"] == selector:
                    return

                step_data = {
                    "action_type": "click",
                    "selector": selector,
                    "tag_name": tag,
                    "visible_text": text,
                    "manual_input_needed": False
                }
                self.recorded_steps.append(step_data)
                step_logged_callback(len(self.recorded_steps), text or tag)

            # Re-expose the native Python bridge callback
            await page.expose_function("registerUniversalClickToPython", capture_hook)

            # 🛠️ THE FIX FOR NAVIGATING TO NEW PAGES:
            # Set up an event listener that catches whenever the site redirects or shifts frames
            page.on("framenavigated", lambda frame: asyncio.create_task(inject_mouse_listeners()))

            # Navigate to the initial url targets entry point
            await page.goto(target_url, wait_until="domcontentloaded")
            await inject_mouse_listeners()

            # Maintain active hook stream listener loops
            while self.is_recording:
                await asyncio.sleep(0.5)
                
            return self.recorded_steps, None