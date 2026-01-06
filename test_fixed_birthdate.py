#!/usr/bin/env python3
"""
Test form submission with CORRECTED birthdate filling method
Based on HTML analysis, birthdate has 3 separate fields:
- Month: dropdown/combobox (id="sid-birthdate__month")
- Day: text input (id="sid-birthdate-day")
- Year: text input (id="sid-birthdate-year")
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.browser import StealthBrowser
from core.template_generator import UniversityDatabase

async def main():
    print("=" * 70)
    print("TESTING CORRECTED BIRTHDATE FILLING")
    print("=" * 70)
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    # Test data - using Stanford
    db = UniversityDatabase()
    all_universities = db.get_all_universities()
    us_universities = [u for u in all_universities if u.get('country') == 'USA']
    
    if not us_universities:
        print("❌ No US universities found")
        return 1
    
    university = us_universities[0]  # Stanford
    test_data = {
        'firstName': 'John',
        'lastName': 'Smith',
        'email': f"john.smith@{university.get('email', 'stanford.edu').split('@')[-1]}",
        'birthMonth': 'June',  # Month name for dropdown
        'birthDay': '15',
        'birthYear': '2000'
    }
    
    print(f"\nUsing university: {university['name']}")
    print(f"Test data: {test_data}\n")
    
    browser = None
    try:
        # Initialize browser
        print("[1] Launching browser...")
        browser = StealthBrowser()
        await browser.initialize()
        page = browser.page  # Use the page created by initialize()
        print("  ✓ Browser ready\n")
        
        # Navigate
        print("[2] Loading page...")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        print("  ✓ Page loaded\n")
        
        # Wait for form
        print("[3] Waiting for form...")
        await page.wait_for_selector('#sid-college-name', state='visible', timeout=10000)
        print("  ✓ Form ready\n")
        
        # Fill university
        print("[4] Selecting university...")
        await page.fill('#sid-college-name', university['name'])
        await page.wait_for_timeout(1000)  # Wait for dropdown
        await page.keyboard.press('ArrowDown')
        await page.keyboard.press('Enter')
        print(f"  ✓ Selected: {university['name']}\n")
        
        # Fill first name
        print("[5] Filling first name...")
        await page.fill('#sid-first-name', test_data['firstName'])
        print(f"  ✓ First name: {test_data['firstName']}\n")
        
        # Fill last name
        print("[6] Filling last name...")
        await page.fill('#sid-last-name', test_data['lastName'])
        print(f"  ✓ Last name: {test_data['lastName']}\n")
        
        # Fill birthdate - CORRECTED METHOD
        print("[7] Filling birthdate (3 separate fields)...")
        
        # Month (dropdown/combobox)
        print(f"  - Month: {test_data['birthMonth']}")
        await page.fill('#sid-birthdate__month', test_data['birthMonth'])
        await page.wait_for_timeout(500)
        await page.keyboard.press('Enter')
        
        # Day (text input)
        print(f"  - Day: {test_data['birthDay']}")
        await page.fill('#sid-birthdate-day', test_data['birthDay'])
        
        # Year (text input)
        print(f"  - Year: {test_data['birthYear']}")
        await page.fill('#sid-birthdate-year', test_data['birthYear'])
        
        print("  ✓ Birthdate filled\n")
        
        # Fill email
        print("[8] Filling email...")
        await page.fill('#sid-email', test_data['email'])
        print(f"  ✓ Email: {test_data['email']}\n")
        
        # Take screenshot before submit
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        await page.screenshot(path=str(output_dir / "ready_to_submit.png"))
        print("  ✓ Screenshot: output/ready_to_submit.png\n")
        
        # Check submit button
        print("[9] Checking submit button...")
        submit_btn = await page.query_selector('#sid-submit-wrapper__collect-info')
        is_disabled = await submit_btn.get_attribute('aria-disabled')
        print(f"  Submit button disabled: {is_disabled}\n")
        
        if is_disabled == 'false':
            print("[10] Submitting form...")
            await submit_btn.click()
            print("  ✓ Form submitted\n")
            
            # Wait for response
            print("[11] Waiting for response...")
            await page.wait_for_timeout(5000)
            
            # Take screenshot after submit
            await page.screenshot(path=str(output_dir / "after_submit.png"))
            print("  ✓ Screenshot: output/after_submit.png\n")
            
            # Check URL for changes
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Check for success indicators
            success_element = await page.query_selector('text="verified"', timeout=2000)
            if success_element:
                print("\n✅ VERIFICATION SUCCESSFUL!")
                return 0
            else:
                print("\n⚠️ Form submitted but verification status unclear")
                print("Check screenshots for results")
                return 0
        else:
            print("\n⚠️ Submit button still disabled after filling all fields")
            print("Possible reasons:")
            print("- Form validation failed")
            print("- Required field missing")
            print("Check screenshot: output/ready_to_submit.png")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Screenshot on error
        if browser and page:
            try:
                await page.screenshot(path=str(Path("output") / "error.png"))
                print("Error screenshot: output/error.png")
            except:
                pass
        
        return 1
        
    finally:
        if browser:
            await browser.close()
            print("\nBrowser closed.")

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
