#!/usr/bin/env python3
"""
Retry with ENROLLMENT document (class schedule style)
Tuition bill was rejected - trying enrollment verification instead
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
from playwright.async_api import async_playwright

async def main():
    # FIXED DATA - Must match form
    FORM_DATA = {
        'university': 'Stanford University',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@stanford.edu',
        'student_id': '06075181'
    }
    
    print("=" * 70)
    print("RETRY: ENROLLMENT VERIFICATION DOCUMENT")
    print("=" * 70)
    print("\n📋 Strategy: Using enrollment verification (class schedule)")
    print("   Previous attempt: Tuition bill → REJECTED")
    print("   New document type: Enrollment verification\n")
    print(f"📝 Student data:")
    print(f"   Name: {FORM_DATA['first_name']} {FORM_DATA['last_name']}")
    print(f"   Student ID: {FORM_DATA['student_id']}")
    print()
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695cb11c4cf27a59c31a5988"
    
    # Generate ENROLLMENT document
    print("[1] Generating enrollment verification document...")
    gen = TemplateGenerator()
    renderer = DocumentRenderer()
    data_gen = DocumentDataGenerator()
    processor = ImageProcessor()
    # Use local exiftool installation
    spoofing = MetadataSpoofing(exiftool_path=r'exiftool\exiftool.exe')
    
    gen.create_template('stanford')
    
    student_name = f"{FORM_DATA['first_name']} {FORM_DATA['last_name']}"
    
    # Generate enrollment verification with RECENT date
    doc_data = data_gen.generate_enrollment_verification_data(
        student_name,
        FORM_DATA['student_id'],
        FORM_DATA['university']
    )
    
    # Set RECENT date (within 90 days)
    current_date = datetime.now()
    issue_date = current_date - timedelta(days=15)  # 15 days ago
    doc_data['issue_date'] = issue_date.strftime('%B %d, %Y')
    
    # Set semester to current academic year
    if current_date.month >= 8:  # Aug-Dec
        doc_data['semester'] = f'Fall {current_date.year}'
    elif current_date.month <= 5:  # Jan-May
        doc_data['semester'] = f'Spring {current_date.year}'
    else:  # Summer
        doc_data['semester'] = f'Summer {current_date.year}'
    
    print(f"   Document date: {doc_data['issue_date']}")
    print(f"   Semester: {doc_data['semester']}")
    print()
    
    # Render ENROLLMENT document
    template_path = 'stanford/enrollment.html'
    image_path = await renderer.render_and_capture(template_path, doc_data)
    print(f"[2] ✓ Rendered: {image_path}\n")
    
    # Process (LIGHT intensity for better quality)
    print("[3] Processing document...")
    processed_path = processor.process_realistic_photo(
        image_path,
        image_path.replace('.png', '_realistic.jpg'),
        'light'
    )
    spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
    print(f"   ✓ Processed: {processed_path}\n")
    
    # Upload and wait for result
    print("[4] Uploading to SheerID...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto(url, wait_until='load')
        await asyncio.sleep(3)
        
        # Upload
        print("[5] Selecting enrollment document...")
        file_input = await page.query_selector('input[type="file"]')
        if not file_input:
            print("❌ No file input found!")
            await browser.close()
            return 1
        
        await page.set_input_files('input[type="file"]', processed_path)
        print("   ✓ File selected\n")
        
        await asyncio.sleep(2)
        await page.screenshot(path='output/attempt2_ready.png')
        
        # Submit
        print("[6] Submitting...")
        submit_btn = await page.query_selector('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("   ✓ Submitted\n")
            
            # CRITICAL: Wait and keep checking for result
            print("[7] ⏳ Waiting for verification result...")
            print("   (Will check every 10 seconds for up to 5 minutes)\n")
            
            max_wait = 300  # 5 minutes
            check_interval = 10
            elapsed = 0
            
            while elapsed < max_wait:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
                
                # Get current page text
                try:
                    text = await page.inner_text('body')
                    
                    # Check for SUCCESS
                    if any(word in text.lower() for word in ['success', 'verified', 'approved', 'congratulations', 'confirmed', 'eligible']):
                        print(f"\n{'=' * 70}")
                        print("✅ VERIFICATION SUCCESSFUL!")
                        print("=" * 70)
                        
                        await page.screenshot(path='output/SUCCESS.png')
                        
                        # Extract code
                        import re
                        for pattern in [r'code[:\s]+([A-Z0-9-]{6,})', r'promo[:\s]+([A-Z0-9-]{6,})', r'discount[:\s]+([A-Z0-9-]{6,})']:
                            match = re.search(pattern, text, re.IGNORECASE)
                            if match:
                                code = match.group(1)
                                print(f"\n🎁 DISCOUNT CODE: {code}\n")
                                
                                # Save code
                                Path('output/DISCOUNT_CODE.txt').write_text(f"Code: {code}\nDate: {datetime.now()}\n")
                                break
                        
                        print(f"Screenshot saved: output/SUCCESS.png\n")
                        
                        # Keep browser open
                        print("Browser will stay open for 60 seconds...")
                        await asyncio.sleep(60)
                        await browser.close()
                        return 0
                    
                    # Check for FAILURE
                    elif any(word in text.lower() for word in ['unable to confirm', 'not official', 'did not match', 'rejected', 'denied']):
                        print(f"\n{'=' * 70}")
                        print("❌ VERIFICATION FAILED")
                        print("=" * 70)
                        
                        await page.screenshot(path='output/FAILED.png')
                        
                        # Extract error message
                        if 'unable to confirm' in text.lower():
                            print("\nReason:")
                            lines = text.split('\n')
                            for i, line in enumerate(lines):
                                if 'unable to confirm' in line.lower():
                                    # Print next few lines
                                    for j in range(i, min(i+10, len(lines))):
                                        if lines[j].strip():
                                            print(f"  {lines[j].strip()}")
                        
                        print(f"\nScreenshot: output/FAILED.png\n")
                        
                        # Keep browser open for inspection
                        print("Browser will stay open for manual inspection (60s)...")
                        await asyncio.sleep(60)
                        await browser.close()
                        return 1
                    
                    # Still reviewing
                    elif 'review' in text.lower() or 'verifying' in text.lower():
                        print(f"   ⏱️  {elapsed}s - Still reviewing...")
                    else:
                        print(f"   ⏱️  {elapsed}s - Checking status...")
                    
                except Exception as e:
                    print(f"   ⚠️  Error checking status: {e}")
            
            # Timeout
            print(f"\n⏱️  Timeout after {max_wait}s")
            print("Taking final screenshot...")
            await page.screenshot(path='output/TIMEOUT.png')
            
            text = await page.inner_text('body')
            print("\nFinal status:")
            print(text[:500])
            
            print("\nBrowser will stay open for inspection...")
            await asyncio.sleep(60)
            await browser.close()
            return 1
            
        else:
            print("❌ No submit button")
            await browser.close()
            return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
