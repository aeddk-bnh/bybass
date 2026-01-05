"""
Module: Form Analyzer
Purpose: Automatically analyze SheerID forms to detect verification type
Technology: Playwright for DOM inspection
"""

import asyncio
from playwright.async_api import async_playwright, Page
from typing import Dict, Optional, List
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SheerIDAnalyzer:
    """
    Analyzes SheerID verification forms to automatically determine:
    - Verification type (student, teacher, military, etc.)
    - Required fields
    - University/institution if applicable
    - Form structure and selectors
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None
    
    async def initialize(self, headless: bool = True):
        """Initialize browser for analysis"""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = await self.context.new_page()
        logger.info("Analyzer initialized")
    
    async def analyze_url(self, url: str) -> Dict:
        """
        Analyze SheerID URL and extract verification details
        
        Args:
            url: SheerID verification URL
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing URL: {url}")
        
        await self.page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)  # Wait for dynamic content
        
        analysis = {
            'url': url,
            'verification_type': await self._detect_verification_type(),
            'university': await self._detect_university(),
            'required_fields': await self._get_required_fields(),
            'form_selectors': await self._extract_selectors(),
            'has_sso': await self._check_sso_option(),
            'has_upload': await self._check_upload_option(),
            'organization': await self._detect_organization()
        }
        
        logger.info(f"Analysis complete: {analysis['verification_type']}")
        return analysis
    
    async def _detect_verification_type(self) -> str:
        """Detect type of verification (student, teacher, military, etc.)"""
        page_text = await self.page.content()
        page_text_lower = page_text.lower()
        
        # Check for keywords
        if 'student' in page_text_lower or 'university' in page_text_lower:
            return 'student'
        elif 'teacher' in page_text_lower or 'educator' in page_text_lower:
            return 'teacher'
        elif 'military' in page_text_lower or 'veteran' in page_text_lower:
            return 'military'
        elif 'first responder' in page_text_lower:
            return 'first_responder'
        elif 'senior' in page_text_lower:
            return 'senior'
        
        return 'unknown'
    
    async def _detect_university(self) -> Optional[str]:
        """Try to detect university name from form or URL"""
        # Check page title
        title = await self.page.title()
        
        # Common university patterns
        uni_patterns = [
            r'(?:university|college|institute)\s+of\s+[\w\s]+',
            r'[\w\s]+\s+(?:university|college|institute)',
        ]
        
        for pattern in uni_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Check for organization field
        try:
            org_input = await self.page.query_selector('input[name*="organization"], input[name*="school"], select[name*="organization"]')
            if org_input:
                # Check if it's a select dropdown
                if await org_input.evaluate('el => el.tagName') == 'SELECT':
                    options = await org_input.evaluate('''el => 
                        Array.from(el.options).slice(0, 5).map(o => o.text)
                    ''')
                    if options:
                        logger.info(f"Found organization options: {options}")
        except:
            pass
        
        return None
    
    async def _get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        required = []
        
        # Find all inputs with required attribute or asterisk
        inputs = await self.page.query_selector_all('input[required], input + label:has-text("*")')
        
        for inp in inputs:
            name = await inp.get_attribute('name')
            placeholder = await inp.get_attribute('placeholder')
            inp_type = await inp.get_attribute('type')
            
            if name:
                required.append(name)
            elif placeholder:
                required.append(placeholder)
        
        # Also check for common fields
        common_fields = ['firstName', 'lastName', 'email', 'birthDate', 'organization']
        for field in common_fields:
            selector = f'input[name="{field}"], input[id="{field}"]'
            element = await self.page.query_selector(selector)
            if element and field not in required:
                required.append(field)
        
        logger.info(f"Required fields: {required}")
        return required
    
    async def _extract_selectors(self) -> Dict[str, str]:
        """Extract CSS selectors for form fields"""
        selectors = {}
        
        # Common field mappings
        field_patterns = {
            'firstName': ['input[name*="first"], input[id*="first"]', 'First Name'],
            'lastName': ['input[name*="last"], input[id*="last"]', 'Last Name'],
            'email': ['input[type="email"], input[name*="email"]', 'Email'],
            'birthDate': ['input[type="date"], input[name*="birth"], input[name*="dob"]', 'Birth Date'],
            'organization': ['select[name*="organization"], select[name*="school"], input[name*="organization"]', 'Organization'],
            'studentId': ['input[name*="student"], input[name*="id"]', 'Student ID'],
            'fileUpload': ['input[type="file"]', 'File Upload'],
            'submitButton': ['button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Verify")', 'Submit']
        }
        
        for field, (selector_patterns, label) in field_patterns.items():
            for pattern in selector_patterns.split(', '):
                try:
                    element = await self.page.query_selector(pattern)
                    if element:
                        # Get the most specific selector
                        element_id = await element.get_attribute('id')
                        element_name = await element.get_attribute('name')
                        
                        if element_id:
                            selectors[field] = f'#{element_id}'
                        elif element_name:
                            selectors[field] = f'[name="{element_name}"]'
                        else:
                            selectors[field] = pattern
                        break
                except:
                    continue
        
        logger.info(f"Extracted selectors: {selectors}")
        return selectors
    
    async def _check_sso_option(self) -> bool:
        """Check if SSO login option is available"""
        sso_keywords = ['single sign', 'sso', 'login with', 'school login', 'university login']
        
        page_text = await self.page.content()
        for keyword in sso_keywords:
            if keyword in page_text.lower():
                logger.info("SSO option detected")
                return True
        
        return False
    
    async def _check_upload_option(self) -> bool:
        """Check if document upload option is available"""
        upload_input = await self.page.query_selector('input[type="file"]')
        
        if upload_input:
            logger.info("Document upload option detected")
            return True
        
        # Check for upload button/link
        upload_text = await self.page.query_selector('button:has-text("Upload"), a:has-text("Upload"), button:has-text("Document")')
        return upload_text is not None
    
    async def _detect_organization(self) -> Optional[str]:
        """Detect the organization offering the discount"""
        # Check page content for brand/company name
        try:
            # Look for logo alt text or brand name
            logo = await self.page.query_selector('img[alt*="logo"], .brand, .company-name')
            if logo:
                alt_text = await logo.get_attribute('alt')
                if alt_text:
                    return alt_text.replace(' logo', '').replace(' Logo', '')
            
            # Check URL domain
            url_domain = self.page.url.split('/')[2]
            return url_domain
        except:
            pass
        
        return None
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Analyzer closed")


async def quick_analyze(url: str) -> Dict:
    """Quick analysis function"""
    analyzer = SheerIDAnalyzer()
    await analyzer.initialize(headless=True)
    
    try:
        result = await analyzer.analyze_url(url)
        return result
    finally:
        await analyzer.close()


if __name__ == "__main__":
    # Test
    async def test():
        url = input("Enter SheerID URL: ")
        result = await quick_analyze(url)
        
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(f"Verification Type: {result['verification_type']}")
        print(f"University: {result['university']}")
        print(f"Organization: {result['organization']}")
        print(f"Has SSO: {result['has_sso']}")
        print(f"Has Upload: {result['has_upload']}")
        print(f"Required Fields: {result['required_fields']}")
        print(f"Selectors: {result['form_selectors']}")
        print("="*60)
    
    asyncio.run(test())
