"""
Module: Browser Automation
Purpose: Stealth browser automation with anti-bot detection bypass
Technology: Playwright + playwright-stealth
"""

import asyncio
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Optional
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthBrowser:
    """
    Playwright-based browser automation with anti-detection measures
    Simulates human behavior and bypasses bot detection systems
    """
    
    def __init__(self, headless: bool = False, proxy: Optional[Dict] = None):
        self.headless = headless
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        
    async def initialize(self):
        """Initialize browser with stealth configuration"""
        playwright = await async_playwright().start()
        
        # Browser launch arguments for stealth
        launch_args = {
            'headless': self.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        }
        
        if self.proxy:
            launch_args['proxy'] = self.proxy
        
        self.browser = await playwright.chromium.launch(**launch_args)
        
        # Create context with realistic fingerprint
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 37.7749, 'longitude': -122.4194}
        )
        
        # Apply stealth scripts
        await self.context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override Chrome detection
            window.chrome = {
                runtime: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        self.page = await self.context.new_page()
        logger.info("Stealth browser initialized")
        
    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to URL with random delay"""
        await asyncio.sleep(random.uniform(1, 3))
        await self.page.goto(url, wait_until=wait_until)
        logger.info(f"Navigated to: {url}")
        
    async def fill_form(self, form_data: Dict[str, str]):
        """
        Fill form with human-like typing simulation
        Handles special fields like birthdate with multiple inputs
        
        Args:
            form_data: Dictionary mapping selector to value
        """
        for selector, value in form_data.items():
            # Special handling for birthdate (3 separate fields)
            if 'birthDate' in selector or 'birthdate' in selector:
                await self._fill_birthdate(selector, value)
                continue
            
            await self.page.wait_for_selector(selector, timeout=10000)
            
            # Random delay before interaction
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Type with random delays between keystrokes
            await self.page.fill(selector, "")  # Clear first
            for char in value:
                await self.page.type(selector, char, delay=random.randint(50, 150))
            
            logger.info(f"Filled field: {selector}")
    
    async def _fill_birthdate(self, base_selector: str, date_value: str):
        """
        Fill birthdate fields (handles both single and multi-field formats)
        
        Args:
            base_selector: Base selector for birthdate field
            date_value: Date in MM/DD/YYYY format
        """
        try:
            # Parse date
            month, day, year = date_value.split('/')
            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_name = month_names[int(month) - 1]
            
            # Try SheerID-style 3-field format
            try:
                # Month dropdown (combobox)
                month_selector = base_selector.replace('birthDate', 'birthdate__month').replace('birth-date', 'birthdate__month')
                if 'sid-birthdate' not in month_selector:
                    month_selector = '#sid-birthdate__month'
                
                await self.page.fill(month_selector, month_name)
                await asyncio.sleep(0.3)
                await self.page.keyboard.press('Enter')
                logger.info(f"Filled month: {month_name}")
                
                # Day input
                day_selector = base_selector.replace('birthDate', 'birthdate-day').replace('birth-date', 'birthdate-day')
                if 'sid-birthdate' not in day_selector:
                    day_selector = '#sid-birthdate-day'
                    
                await self.page.fill(day_selector, day)
                logger.info(f"Filled day: {day}")
                
                # Year input
                year_selector = base_selector.replace('birthDate', 'birthdate-year').replace('birth-date', 'birthdate-year')
                if 'sid-birthdate' not in year_selector:
                    year_selector = '#sid-birthdate-year'
                    
                await self.page.fill(year_selector, year)
                logger.info(f"Filled year: {year}")
                
            except Exception as e:
                # Fallback to single field
                logger.info(f"3-field birthdate failed, trying single field: {e}")
                await self.page.wait_for_selector(base_selector, timeout=5000)
                await self.page.fill(base_selector, date_value)
                logger.info(f"Filled birthdate (single field): {date_value}")
                
        except Exception as e:
            logger.error(f"Error filling birthdate: {e}")
            # Last resort: try the base selector as-is
            try:
                await self.page.fill(base_selector, date_value)
            except:
                pass
    
    async def intercept_sso_requests(self):
        """
        Intercept SSO authentication requests to force document upload flow
        """
        async def handle_route(route, request):
            # Block SSO authentication endpoints
            if any(keyword in request.url for keyword in ['sso', 'saml', 'oauth', 'login.microsoftonline']):
                logger.info(f"Blocked SSO request: {request.url}")
                await route.abort()
            else:
                await route.continue_()
        
        await self.page.route("**/*", handle_route)
        logger.info("SSO request interception enabled")
    
    async def upload_document(self, file_path: str, selector: str = 'input[type="file"]'):
        """
        Upload document to file input
        
        Args:
            file_path: Path to file to upload
            selector: CSS selector for file input
        """
        await self.page.wait_for_selector(selector, timeout=10000)
        await self.page.set_input_files(selector, file_path)
        logger.info(f"Uploaded file: {file_path}")
        
    async def wait_for_approval(self, approval_selector: str, timeout: int = 60000) -> bool:
        """
        Poll for approval status
        
        Args:
            approval_selector: Selector indicating approval
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if approved, False otherwise
        """
        try:
            await self.page.wait_for_selector(approval_selector, timeout=timeout)
            logger.info("Approval detected")
            return True
        except:
            logger.warning("Approval timeout")
            return False
    
    async def extract_discount_code(self, code_selector: str) -> str:
        """
        Extract discount code from page
        
        Args:
            code_selector: CSS selector for discount code element
            
        Returns:
            Discount code string
        """
        element = await self.page.wait_for_selector(code_selector)
        code = await element.inner_text()
        logger.info(f"Extracted code: {code}")
        return code.strip()
    
    async def screenshot(self, path: str, full_page: bool = False):
        """Take screenshot of current page"""
        await self.page.screenshot(path=path, full_page=full_page)
        logger.info(f"Screenshot saved: {path}")
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")


async def main_example():
    """Example usage of StealthBrowser"""
    browser = StealthBrowser(headless=False)
    await browser.initialize()
    
    # Example workflow
    await browser.navigate("https://example-sheerid.com/verify")
    
    # Fill form
    await browser.fill_form({
        '#firstName': 'John',
        '#lastName': 'Doe',
        '#email': 'john.doe@stanford.edu'
    })
    
    # Enable SSO interception
    await browser.intercept_sso_requests()
    
    # Upload document
    await browser.upload_document('output/document.jpg')
    
    # Wait and extract code
    if await browser.wait_for_approval('.approval-message'):
        code = await browser.extract_discount_code('.discount-code')
        print(f"Success! Code: {code}")
    
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main_example())
