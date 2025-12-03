from playwright.sync_api import sync_playwright
import json
import time
import os

class SandboxAnalyzer:
    def __init__(self):
        self.screenshot_dir = "/data/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def analyze_url(self, url: str):
        results = {
            "url": url,
            "title": None,
            "has_login_form": False,
            "screenshot_path": None,
            "external_resources": [],
            "error": None
        }

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set timeout to 10 seconds for speed
                page.set_default_timeout(10000)
                
                response = page.goto(url)
                page.wait_for_load_state("networkidle")
                
                results["title"] = page.title()
                
                # Check for login forms
                login_keywords = ["password", "login", "signin", "user", "email"]
                inputs = page.query_selector_all("input")
                for inp in inputs:
                    attr_type = inp.get_attribute("type")
                    attr_name = inp.get_attribute("name")
                    if attr_type == "password" or (attr_name and any(k in attr_name.lower() for k in login_keywords)):
                        results["has_login_form"] = True
                        break
                
                # Take screenshot
                filename = f"{int(time.time())}_{hash(url)}.png"
                path = os.path.join(self.screenshot_dir, filename)
                page.screenshot(path=path)
                results["screenshot_path"] = path

                browser.close()
                
        except Exception as e:
            results["error"] = str(e)

        return results

if __name__ == "__main__":
    # Test run
    analyzer = SandboxAnalyzer()
    print(json.dumps(analyzer.analyze_url("https://example.com"), indent=2))
