#!/usr/bin/env python3
"""
Complete flow với verification ID mới
- Tự động phát hiện trạng thái trang
- Fill form nếu cần
- Upload enrollment document
- Đợi kết quả
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from core.template_generator import TemplateGenerator
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing
from core.browser import StealthBrowser
from playwright.async_api import async_playwright

async def main():
    # FIXED DATA
    FORM_DATA = {
        'university': 'Stanford University',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@stanford.edu',
        'student_id': '06075181',
        'birthdate': '06/15/2000'
    }
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695cb11c4cf27a59c31a5988"
    
    print("=" * 70)
    print("COMPLETE FLOW - NEW VERIFICATION ID")
    print("=" * 70)
    print(f"\n📝 Student: {FORM_DATA['first_name']} {FORM_DATA['last_name']}")
    print(f"   ID: {FORM_DATA['student_id']}")
    print(f"   University: {FORM_DATA['university']}\n")
    
    # Generate enrollment document
    print("[1] Generating enrollment verification document...")
    gen = TemplateGenerator()
    renderer = DocumentRenderer()
    data_gen = DocumentDataGenerator()
    processor = ImageProcessor()
    spoofing = MetadataSpoofing(exiftool_path=r'exiftool\exiftool.exe')
    
    # Create document data
    doc_data = {
        'name': f"{FORM_DATA['first_name']} {FORM_DATA['last_name']}",
        'id': FORM_DATA['student_id'],
        'program': 'Computer Science',
    }
    
    current_date = datetime.now()
    issue_date = current_date - timedelta(days=15)
    doc_data['issue_date'] = issue_date.strftime('%B %d, %Y')
    
    if current_date.month >= 8:
        doc_data['semester'] = f'Fall {current_date.year}'
    elif current_date.month <= 5:
        doc_data['semester'] = f'Spring {current_date.year}'
    else:
        doc_data['semester'] = f'Summer {current_date.year}'
    
    print(f"   Document: {doc_data['semester']} Enrollment")
    print(f"   Issue date: {doc_data['issue_date']}\n")
    
    # Render
    template_path = 'stanford/enrollment.html'
    image_path = await renderer.render_and_capture(template_path, doc_data)
    print(f"[2] ✓ Rendered: {image_path}\n")
    
    # Process with LIGHT intensity
    print("[3] Processing document (light intensity)...")
    processed_path = processor.process_realistic_photo(
        image_path,
        image_path.replace('.png', '_realistic.jpg'),
        'light'
    )
    spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
    print(f"   ✓ Processed: {processed_path}\n")
    
    # Navigate and handle flow
    print("[4] Opening SheerID page...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto(url, wait_until='load')
        await asyncio.sleep(3)
        
        # Check page state
        await page.screenshot(path='output/1_initial_state.png')
        
        # Check for form fields
        first_name_input = await page.query_selector('#sid-first-name')
        file_input = await page.query_selector('input[type="file"]')
        
        if first_name_input:
            # Form exists - fill it
            print("[5] Form detected - filling...")
            
            await page.fill('#sid-first-name', FORM_DATA['first_name'])
            await page.fill('#sid-last-name', FORM_DATA['last_name'])
            await page.fill('#sid-email', FORM_DATA['email'])
            
            # Birthdate (3 fields - combobox + inputs)
            parts = FORM_DATA['birthdate'].split('/')
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            # Month (combobox - type and select)
            await page.fill('#sid-birthdate__month', month_names[int(parts[0])])
            await asyncio.sleep(0.5)
            await page.keyboard.press('ArrowDown')
            await page.keyboard.press('Enter')
            
            await page.fill('#sid-birthdate-day', parts[1])
            await page.fill('#sid-birthdate-year', parts[2])
            
            # University
            await page.fill('#sid-organization', FORM_DATA['university'])
            await asyncio.sleep(1)
            await page.keyboard.press('ArrowDown')
            await page.keyboard.press('Enter')
            
            # Student ID
            await page.fill('#sid-student-id', FORM_DATA['student_id'])
            
            await page.screenshot(path='output/2_form_filled.png')
            print("   ✓ Form filled\n")
            
            # Submit form
            print("[6] Submitting form...")
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                await asyncio.sleep(5)
                await page.screenshot(path='output/3_after_submit.png')
                print("   ✓ Submitted\n")
        
        # Now check for upload field
        print("[7] Checking for upload field...")
        await asyncio.sleep(2)
        file_input = await page.query_selector('input[type="file"]')
        
        if not file_input:
            print("❌ No upload field found!")
            print("Current page state saved to output/3_after_submit.png")
            input("Press Enter to close browser...")
            await browser.close()
            return 1
        
        print("[8] Upload field found - uploading document...")
        await page.set_input_files('input[type="file"]', processed_path)
        print("   ✓ File selected\n")
        
        await asyncio.sleep(2)
        await page.screenshot(path='output/4_file_selected.png')
        
        # Submit upload
        print("[9] Submitting upload...")
        submit_btn = await page.query_selector('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("   ✓ Submitted\n")
            
            # Wait for result
            print("[10] ⏳ Waiting for verification result...")
            print("    (Checking every 10 seconds for up to 5 minutes)\n")
            
            max_wait = 300
            check_interval = 10
            elapsed = 0
            
            while elapsed < max_wait:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
                
                print(f"   ⏱️  {elapsed}s - Checking status...")
                
                try:
                    text = await page.inner_text('body')
                    
                    # Success
                    if any(word in text.lower() for word in ['success', 'verified', 'approved', 'congratulations', 'eligible']):
                        print(f"\n{'=' * 70}")
                        print("✅ VERIFICATION SUCCESSFUL!")
                        print("=" * 70)
                        
                        await page.screenshot(path='output/SUCCESS.png')
                        
                        import re
                        for pattern in [r'code[:\s]+([A-Z0-9-]{6,})', r'promo[:\s]+([A-Z0-9-]{6,})', r'discount[:\s]+([A-Z0-9-]{6,})']:
                            match = re.search(pattern, text, re.IGNORECASE)
                            if match:
                                code = match.group(1)
                                print(f"\n🎁 DISCOUNT CODE: {code}\n")
                                Path('output/DISCOUNT_CODE.txt').write_text(f"Code: {code}\nDate: {datetime.now()}\n")
                                break
                        
                        input("Press Enter to close browser...")
                        await browser.close()
                        return 0
                    
                    # Failure
                    if any(word in text.lower() for word in ['reject', 'denied', 'unable to verify', 'try again', 'error']):
                        print(f"\n{'=' * 70}")
                        print("❌ VERIFICATION FAILED")
                        print("=" * 70)
                        print(f"\nReason: Check output/FAILED.png\n")
                        
                        await page.screenshot(path='output/FAILED.png')
                        
                        # Save error details
                        Path('output/ERROR_DETAILS.txt').write_text(f"Failed at: {datetime.now()}\nPage text:\n{text}\n")
                        
                        input("Press Enter to close browser...")
                        await browser.close()
                        return 1
                    
                    # Still reviewing
                    if 'review' in text.lower():
                        print(f"   ⏱️  {elapsed}s - Still reviewing...")
                
                except Exception as e:
                    print(f"   Error checking status: {e}")
            
            # Timeout
            print(f"\n⏱️  Timeout after {max_wait}s")
            print("Taking final screenshot...\n")
            await page.screenshot(path='output/TIMEOUT.png')
            
            text = await page.inner_text('body')
            print(f"Final status:\n{text[:500]}\n")
            
            input("Press Enter to close browser...")
            await browser.close()
            return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
