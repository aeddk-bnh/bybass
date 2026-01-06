#!/usr/bin/env python3
"""
Upload với data CHÍNH XÁC đã submit trong form
CRITICAL: Data phải match 100% với form đã submit
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.template_generator import TemplateGenerator
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing
from playwright.async_api import async_playwright

async def main():
    # FIXED DATA - Must match what was submitted in form
    # (Lấy từ form đã submit lần trước)
    FORM_DATA = {
        'university': 'Stanford University',
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@stanford.edu',
        'birth_date': '06/15/2000',
        # Generate student ID theo format Stanford
        'student_id': '06075181'  # Fixed ID
    }
    
    print("=" * 70)
    print("UPLOAD WITH MATCHING DATA")
    print("=" * 70)
    print(f"\n📝 Using EXACT data from form:")
    print(f"   Name: {FORM_DATA['first_name']} {FORM_DATA['last_name']}")
    print(f"   Email: {FORM_DATA['email']}")
    print(f"   Student ID: {FORM_DATA['student_id']}")
    print()
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    # Generate document with MATCHING data
    print("[1] Generating document with matching data...")
    gen = TemplateGenerator()
    renderer = DocumentRenderer()
    data_gen = DocumentDataGenerator()
    processor = ImageProcessor()
    spoofing = MetadataSpoofing()
    
    # Create Stanford template
    gen.create_template('stanford')
    
    # Generate data with EXACT name and recent date
    student_name = f"{FORM_DATA['first_name']} {FORM_DATA['last_name']}"
    
    # Generate RECENT tuition bill (within 90 days)
    doc_data = data_gen.generate_tuition_bill_data(
        student_name, 
        FORM_DATA['student_id'], 
        FORM_DATA['university']
    )
    
    # CRITICAL: Ensure date is within 90 days
    from datetime import datetime, timedelta
    current_date = datetime.now()
    recent_date = current_date - timedelta(days=30)  # 30 days ago
    doc_data['issue_date'] = recent_date.strftime('%B %d, %Y')
    doc_data['due_date'] = (current_date + timedelta(days=30)).strftime('%B %d, %Y')
    
    print(f"   Document date: {doc_data['issue_date']}")
    print()
    
    # Render
    template_path = 'stanford/bill.html'
    image_path = await renderer.render_and_capture(template_path, doc_data)
    print(f"[2] ✓ Rendered: {image_path}\n")
    
    # Process
    print("[3] Processing document...")
    processed_path = processor.process_realistic_photo(
        image_path,
        image_path.replace('.png', '_realistic.jpg'),
        'medium'
    )
    spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
    print(f"   ✓ Processed: {processed_path}\n")
    
    # Upload
    print("[4] Uploading to SheerID...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto(url, wait_until='load')
        await asyncio.sleep(3)
        
        # Upload file
        print("[5] Selecting file...")
        file_input = await page.query_selector('input[type="file"]')
        if not file_input:
            print("❌ No file input found!")
            return 1
        
        await page.set_input_files('input[type="file"]', processed_path)
        print("   ✓ File selected\n")
        
        await asyncio.sleep(2)
        await page.screenshot(path='output/upload_ready.png')
        
        # Submit
        print("[6] Submitting...")
        submit_btn = await page.query_selector('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("   ✓ Submitted\n")
            
            # Wait for verification (60 seconds)
            print("[7] ⏳ Waiting for verification...")
            for i in range(12):
                await asyncio.sleep(5)
                print(f"   ⏱️  {(i+1)*5}s...")
            print()
            
            # Check result
            await page.screenshot(path='output/verification_result.png')
            
            text = await page.inner_text('body')
            
            # Check for success
            if any(word in text.lower() for word in ['success', 'verified', 'approved', 'congratulations', 'confirmed']):
                print("=" * 70)
                print("✅ VERIFICATION SUCCESSFUL!")
                print("=" * 70)
                
                # Extract code
                import re
                for pattern in [r'code[:\s]+([A-Z0-9]{6,})', r'promo[:\s]+([A-Z0-9]{6,})']:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        print(f"🎁 Code: {match.group(1)}")
                        break
                
                return 0
            elif 'unable to confirm' in text.lower() or 'did not match' in text.lower():
                print("=" * 70)
                print("❌ VERIFICATION FAILED - Data Mismatch")
                print("=" * 70)
                print("\nReasons:")
                if 'first name' in text.lower():
                    print("  • First name mismatch")
                if 'last name' in text.lower():
                    print("  • Last name mismatch")
                if 'date requirements' in text.lower():
                    print("  • Date requirements not met")
                
                print(f"\nDocument generated:")
                print(f"  Name: {student_name}")
                print(f"  Date: {doc_data['issue_date']}")
                print(f"\nForm submitted with:")
                print(f"  Name: {FORM_DATA['first_name']} {FORM_DATA['last_name']}")
                
                return 1
            else:
                print("⚠️ Unknown status - check screenshot")
                print(text[:500])
                return 1
        else:
            print("❌ No submit button")
            return 1
        
        print("\nBrowser stays open for inspection...")
        try:
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            pass
        
        await browser.close()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
