#!/usr/bin/env python3
"""
Clean version - Fill and submit form with corrected birthdate method
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.browser import StealthBrowser
from core.template_generator import UniversityDatabase

async def main():
    print("=" * 70)
    print("SHEERID FORM AUTO-FILL & SUBMIT")
    print("=" * 70)
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    # Get US universities
    db = UniversityDatabase()
    us_universities = [u for u in db.get_all_universities() if u.get('country') == 'USA']
    
    if not us_universities:
        print("❌ No US universities found")
        return 1
    
    university = us_universities[0]  # Stanford
    test_data = {
        'firstName': 'John',
        'lastName': 'Smith',
        'email': 'john.smith@stanford.edu',
        'birthMonth': 'June',
        'birthDay': '15',
        'birthYear': '2000'
    }
    
    print(f"\n📚 University: {university['name']}")
    print(f"👤 Name: {test_data['firstName']} {test_data['lastName']}")
    print(f"📧 Email: {test_data['email']}")
    print(f"🎂 DOB: {test_data['birthMonth']} {test_data['birthDay']}, {test_data['birthYear']}\n")
    
    browser = None
    try:
        # Initialize
        print("[1] Launching browser...")
        browser = StealthBrowser()
        await browser.initialize()
        page = browser.page
        print("  ✓ Ready\n")
        
        # Navigate
        print("[2] Loading page...")
        await page.goto(url, wait_until='load', timeout=30000)
        await page.wait_for_timeout(3000)  # Extra wait
        print("  ✓ Loaded\n")
        
        # Wait for form
        print("[3] Waiting for form...")
        await page.wait_for_selector('#sid-college-name', state='visible', timeout=10000)
        print("  ✓ Form ready\n")
        
        # Fill university
        print(f"[4] Selecting: {university['name']}...")
        await page.fill('#sid-college-name', university['name'])
        await page.wait_for_timeout(1000)
        await page.keyboard.press('ArrowDown')
        await page.keyboard.press('Enter')
        print("  ✓ Selected\n")
        
        # Fill name
        print("[5] Filling name...")
        await page.fill('#sid-first-name', test_data['firstName'])
        await page.fill('#sid-last-name', test_data['lastName'])
        print("  ✓ Done\n")
        
        # Fill birthdate (3 fields)
        print("[6] Filling birthdate...")
        await page.fill('#sid-birthdate__month', test_data['birthMonth'])
        await page.wait_for_timeout(500)
        await page.keyboard.press('Enter')
        await page.fill('#sid-birthdate-day', test_data['birthDay'])
        await page.fill('#sid-birthdate-year', test_data['birthYear'])
        print("  ✓ Done\n")
        
        # Fill email
        print("[7] Filling email...")
        await page.fill('#sid-email', test_data['email'])
        print("  ✓ Done\n")
        
        # Screenshot
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        await page.screenshot(path=str(output_dir / "ready_to_submit.png"))
        print("  📸 Screenshot: output/ready_to_submit.png\n")
        
        # Submit
        print("[8] Submitting form...")
        submit_btn = await page.query_selector('#sid-submit-wrapper__collect-info')
        is_disabled = await submit_btn.get_attribute('aria-disabled')
        
        if is_disabled == 'false':
            await submit_btn.click()
            print("  ✓ Submitted\n")
            
            # Wait and screenshot
            print("[9] Waiting for response...")
            await page.wait_for_timeout(5000)
            await page.screenshot(path=str(output_dir / "after_submit.png"))
            print("  📸 Screenshot: output/after_submit.png\n")
            
            print("=" * 70)
            print("✅ COMPLETED - Check screenshots for results")
            print("=" * 70)
            return 0
        else:
            print("  ⚠️ Submit button still disabled\n")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
        
    finally:
        if browser:
            await browser.close()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
