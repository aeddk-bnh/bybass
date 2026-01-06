#!/usr/bin/env python3
"""
Complete flow test: Fill form → Submit → Upload document
Tests the entire verification process with birthdate fix
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.browser import StealthBrowser
from core.template_generator import UniversityDatabase, TemplateGenerator
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing
import random

async def main():
    print("=" * 70)
    print("COMPLETE VERIFICATION FLOW TEST")
    print("=" * 70)
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    # Get US university
    db = UniversityDatabase()
    us_universities = [u for u in db.get_all_universities() if u.get('country') == 'USA']
    
    if not us_universities:
        print("❌ No US universities found")
        return 1
    
    university = us_universities[0]  # Stanford
    
    # Generate student data
    first_name = 'John'
    last_name = 'Smith'
    student_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@stanford.edu"
    
    year = random.randint(2020, 2024)
    num = random.randint(1, 9999)
    student_id = university['id_format'].format(year=year, num=num)
    
    print(f"\n📚 University: {university['name']}")
    print(f"👤 Name: {student_name}")
    print(f"📧 Email: {email}")
    print(f"🆔 Student ID: {student_id}")
    print(f"🎂 DOB: June 15, 2000\n")
    
    browser = None
    try:
        # Initialize browser
        print("[1] Launching browser...")
        browser = StealthBrowser(headless=False)  # Visible for debugging
        await browser.initialize()
        page = browser.page
        print("  ✓ Ready\n")
        
        # Navigate
        print("[2] Loading page...")
        await page.goto(url, wait_until='load', timeout=30000)
        await asyncio.sleep(3)  # Wait for JS to render
        print("  ✓ Loaded\n")
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Check if we're already on upload page (form was submitted before)
        print("[3] Detecting page type...")
        upload_input = await page.query_selector('input[type="file"]')
        
        if upload_input:
            print("  ✓ Already on upload page!\n")
            # Skip form filling, go directly to upload
        else:
            # Wait for form
            print("  → Form page detected, filling...\n")
            await page.wait_for_selector('#sid-college-name', state='visible', timeout=15000)
            print("  ✓ Form ready\n")
        if upload_input:
            print("  ✓ Already on upload page!\n")
            # Skip form filling, go directly to upload
        else:
            # Wait for form
            print("  → Form page detected, filling...\n")
            await page.wait_for_selector('#sid-college-name', state='visible', timeout=15000)
            print("  ✓ Form ready\n")
        
            # Fill university
            print(f"[4] Selecting: {university['name']}...")
            await page.fill('#sid-college-name', university['name'])
            await asyncio.sleep(1)
            await page.keyboard.press('ArrowDown')
            await page.keyboard.press('Enter')
            print("  ✓ Selected\n")
            
            # Fill form fields
            print("[5] Filling personal info...")
            await page.fill('#sid-first-name', first_name)
            await page.fill('#sid-last-name', last_name)
            print("  ✓ Name filled\n")
            
            # Fill birthdate - 3 separate fields
            print("[6] Filling birthdate...")
            await page.fill('#sid-birthdate__month', 'June')
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            await page.fill('#sid-birthdate-day', '15')
            await page.fill('#sid-birthdate-year', '2000')
            print("  ✓ Birthdate filled\n")
            
            # Fill email
            print("[7] Filling email...")
            await page.fill('#sid-email', email)
            print("  ✓ Email filled\n")
            
            # Screenshot before submit
            await page.screenshot(path=str(output_dir / "1_ready_to_submit.png"))
            
            # Submit
            print("[8] Submitting form...")
            submit_btn = await page.query_selector('#sid-submit-wrapper__collect-info')
            is_disabled = await submit_btn.get_attribute('aria-disabled')
            
            if is_disabled == 'true':
                print("  ⚠️ Submit button disabled - checking form validation...")
                return 1
            
            await submit_btn.click()
            print("  ✓ Submitted\n")
            
            # Wait for page transition
            print("[9] Waiting for response...")
            await asyncio.sleep(3)
            await page.screenshot(path=str(output_dir / "2_after_submit.png"))
        
        # Now check for upload page (whether we came from form or directly)
        print("[10] Checking for upload page...")
        upload_input = await page.query_selector('input[type="file"]')
        has_upload = upload_input is not None
        
        if has_upload:
            print("  ✓ Upload page detected!\n")
            
            # Generate document
            print("[11] Generating document...")
            gen = TemplateGenerator()
            renderer = DocumentRenderer()
            data_gen = DocumentDataGenerator()
            processor = ImageProcessor()
            spoofing = MetadataSpoofing()
            
            # Ensure template exists
            template_key = university['key']
            gen.create_template(template_key)
            
            # Generate document data
            template_file = 'bill.html' if university['type'] == 'bill' else 'enrollment.html'
            template_path = f"{template_key}/{template_file}"
            
            if university['type'] == 'bill':
                doc_data = data_gen.generate_tuition_bill_data(student_name, student_id, university['name'])
            else:
                doc_data = data_gen.generate_enrollment_verification_data(student_name, student_id, university['name'])
            
            # Render
            image_path = await renderer.render_and_capture(template_path, doc_data)
            print(f"  ✓ Document rendered: {image_path}\n")
            
            # Process to look realistic
            print("[12] Processing document...")
            processed_path = processor.process_realistic_photo(
                image_path,
                image_path.replace('.png', '_realistic.jpg'),
                'medium'
            )
            spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
            print(f"  ✓ Processed: {processed_path}\n")
            
            # Upload
            print("[13] Uploading document...")
            await page.set_input_files('input[type="file"]', processed_path)
            print("  ✓ File selected\n")
            
            # Wait a bit for upload to process
            await asyncio.sleep(2)
            await page.screenshot(path=str(output_dir / "3_after_upload.png"))
            
            # Submit upload form
            print("[14] Submitting upload...")
            upload_submit = await page.query_selector('button[type="submit"]')
            if upload_submit:
                await upload_submit.click()
                print("  ✓ Upload submitted\n")
                
                # CRITICAL: Wait ~1 minute for verification process
                print("[15] ⏳ Waiting for verification (this takes ~60 seconds)...")
                for i in range(12):  # 12 x 5 = 60 seconds
                    await asyncio.sleep(5)
                    print(f"  ⏱️  {(i+1)*5} seconds elapsed...")
                
                print("  ✓ Verification wait complete\n")
                
                # Take screenshot of result
                await page.screenshot(path=str(output_dir / "4_final_result.png"))
                
                # Check for success
                print("[16] Checking verification result...")
                final_content = await page.content()
                final_text = await page.inner_text('body')
                
                success_keywords = ['success', 'verified', 'approved', 'congratulations', 'confirmed']
                is_success = any(word in final_content.lower() for word in success_keywords)
                
                if is_success:
                    print("\n" + "=" * 70)
                    print("✅ VERIFICATION SUCCESSFUL!")
                    print("=" * 70)
                    
                    # Try to extract code
                    try:
                        import re
                        # Look for discount/promo codes
                        code_patterns = [
                            r'code[:\s]+([A-Z0-9]{6,})',
                            r'promo[:\s]+([A-Z0-9]{6,})',
                            r'discount[:\s]+([A-Z0-9]{6,})',
                            r'\b([A-Z0-9]{8,12})\b'
                        ]
                        
                        for pattern in code_patterns:
                            match = re.search(pattern, final_text, re.IGNORECASE)
                            if match:
                                print(f"🎁 Discount Code: {match.group(1)}")
                                break
                        else:
                            print("ℹ️  No code found (might be on next page)")
                    except:
                        pass
                    
                    # Save result
                    with open(output_dir / "verification_result.txt", 'w') as f:
                        f.write(f"University: {university['name']}\n")
                        f.write(f"Student: {student_name}\n")
                        f.write(f"Email: {email}\n")
                        f.write(f"Status: VERIFIED\n")
                        f.write(f"Timestamp: {Path(output_dir / '4_final_result.png').stat().st_mtime}\n")
                    
                    return 0
                else:
                    print("\n" + "=" * 70)
                    print("⚠️ VERIFICATION STATUS UNCLEAR")
                    print("=" * 70)
                    print("Checking for error messages...")
                    
                    # Check for common error messages
                    error_keywords = ['error', 'failed', 'unable', 'invalid', 'rejected', 'denied']
                    has_error = any(word in final_content.lower() for word in error_keywords)
                    
                    if has_error:
                        print("❌ Verification appears to have failed")
                        print("Check screenshot: output/4_final_result.png")
                    else:
                        print("ℹ️  Still processing or requires additional steps")
                        print("Check screenshots in output/ folder")
                    
                    return 0
            else:
                print("  ⚠️ No submit button found after upload")
                return 1
        else:
            print("  ℹ️ No upload page (might be instant verification or error)")
            
            # Check for success
            if any(word in page_content.lower() for word in ['success', 'verified', 'approved']):
                print("\n✅ Instant verification!")
                return 0
            else:
                print("\n⚠️ Unknown state - check screenshot")
                return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Screenshot on error
        if browser and browser.page:
            try:
                await browser.page.screenshot(path=str(Path("output") / "error.png"))
                print("Error screenshot: output/error.png")
            except:
                pass
        
        return 1
        
    finally:
        if browser:
            # Keep browser open for manual inspection
            print("\n⏸️  Browser will stay open for 30 seconds...")
            print("Press Ctrl+C to close immediately")
            try:
                await asyncio.sleep(30)
            except KeyboardInterrupt:
                pass
            await browser.close()

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
