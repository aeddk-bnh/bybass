#!/usr/bin/env python3
"""
UNIFIED FLOW - Auto-detect state and handle verification
- Detects if form needs filling or already on upload page
- Uses Student ID Card with expiration date (accepted document type)
- Auto-retry on failure with new document
- Accepts URL from command line or uses default
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import os

sys.path.insert(0, str(Path(__file__).parent))

from core.browser import StealthBrowser
from core.template_generator import TemplateGenerator
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing

# Default URL if not provided
DEFAULT_URL = 'https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695cb11c4cf27a59c31a5988'

# Fixed student data
STUDENT_DATA = {
    'first_name': 'John',
    'last_name': 'Smith',
    'email': 'john.smith@stanford.edu',
    'student_id': '06075181',
    'birthdate_month': 'June',
    'birthdate_day': '15',
    'birthdate_year': '2000',
    'university': 'Stanford University'
}

async def generate_student_id_document():
    """Generate Student ID Card document with expiration date"""
    print("\n📄 Generating Student ID Card...")
    
    gen = TemplateGenerator()
    renderer = DocumentRenderer()
    processor = ImageProcessor()
    spoofing = MetadataSpoofing(exiftool_path=r'exiftool\exiftool.exe')
    
    # Create template if needed
    gen.create_template('stanford')
    
    # Document data
    doc_data = {
        'name': f"{STUDENT_DATA['first_name']} {STUDENT_DATA['last_name']}",
        'id': STUDENT_DATA['student_id'],
        'program': 'Computer Science',
    }
    
    current_date = datetime.now()
    
    # Issue date: 6 months ago
    issue_date = current_date - timedelta(days=180)
    doc_data['issue_date'] = issue_date.strftime('%B %d, %Y')
    
    # CRITICAL: Expiration date (required for Student ID)
    expiration_date = current_date + timedelta(days=180)  # Valid for 6 months from now
    doc_data['expiration_date'] = expiration_date.strftime('%m/%d/%Y')
    
    # Academic year
    if current_date.month >= 8:
        doc_data['academic_year'] = f'{current_date.year}-{current_date.year + 1}'
    else:
        doc_data['academic_year'] = f'{current_date.year - 1}-{current_date.year}'
    
    print(f"   Academic Year: {doc_data['academic_year']}")
    print(f"   Expiration: {doc_data['expiration_date']}")
    
    # Render
    template_path = 'stanford/student_id.html'
    image_path = await renderer.render_and_capture(template_path, doc_data)
    print(f"   ✓ Rendered: {image_path}")
    
    # Process with LIGHT intensity (best quality)
    processed_path = processor.process_realistic_photo(
        image_path,
        image_path.replace('.png', '_realistic.jpg'),
        'light'  # Low noise, high JPEG quality
    )
    
    # Spoof metadata
    spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
    print(f"   ✓ Processed: {processed_path}\n")
    
    return processed_path

async def fill_form_if_needed(page):
    """Check if form exists and fill it"""
    print("[Form Check] Detecting page state...")
    
    # Check for upload input first
    upload_input = await page.query_selector('input[type="file"]')
    if upload_input:
        print("   ✓ Already on upload page - skipping form\n")
        return True
    
    # Check for form
    first_name_field = await page.query_selector('#sid-first-name')
    if not first_name_field:
        print("   ⚠️ No form or upload page detected")
        return False
    
    print("   → Form detected - filling...\n")
    
    # Fill university
    print("[1] Selecting university...")
    await page.fill('#sid-college-name', STUDENT_DATA['university'])
    await asyncio.sleep(1)
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter')
    print("   ✓ Selected\n")
    
    # Fill name
    print("[2] Filling name...")
    await page.fill('#sid-first-name', STUDENT_DATA['first_name'])
    await page.fill('#sid-last-name', STUDENT_DATA['last_name'])
    print("   ✓ Name filled\n")
    
    # Fill birthdate
    print("[3] Filling birthdate...")
    await page.fill('#sid-birthdate__month', STUDENT_DATA['birthdate_month'])
    await asyncio.sleep(0.5)
    await page.keyboard.press('Enter')
    await page.fill('#sid-birthdate-day', STUDENT_DATA['birthdate_day'])
    await page.fill('#sid-birthdate-year', STUDENT_DATA['birthdate_year'])
    print("   ✓ Birthdate filled\n")
    
    # Fill email
    print("[4] Filling email...")
    await page.fill('#sid-email', STUDENT_DATA['email'])
    print("   ✓ Email filled\n")
    
    # Screenshot before submit
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    await page.screenshot(path=str(output_dir / "1_form_filled.png"))
    
    # Submit
    print("[5] Submitting form...")
    submit_btn = await page.query_selector('#sid-submit-wrapper__collect-info')
    if not submit_btn:
        print("   ❌ Submit button not found")
        return False
    
    is_disabled = await submit_btn.get_attribute('aria-disabled')
    if is_disabled == 'true':
        print("   ❌ Submit button disabled")
        return False
    
    await submit_btn.click()
    print("   ✓ Form submitted\n")
    
    # Wait for navigation
    await asyncio.sleep(5)
    await page.screenshot(path=str(output_dir / "2_after_form_submit.png"))
    
    return True

async def upload_document_and_wait(page, document_path, attempt=1):
    """Upload document and wait for verification result"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n[Upload - Attempt {attempt}] Checking for upload field...")
    upload_input = await page.query_selector('input[type="file"]')
    
    if not upload_input:
        print("   ❌ No upload field found")
        await page.screenshot(path=str(output_dir / f"error_no_upload_attempt{attempt}.png"))
        return None
    
    print("   ✓ Upload field found\n")
    
    # Upload
    print(f"[1] Uploading document (attempt {attempt})...")
    await page.set_input_files('input[type="file"]', document_path)
    print("   ✓ File selected\n")
    
    await asyncio.sleep(2)
    await page.screenshot(path=str(output_dir / f"3_file_uploaded_attempt{attempt}.png"))
    
    # Submit
    print("[2] Submitting upload...")
    submit_btn = await page.query_selector('button[type="submit"]')
    if not submit_btn:
        print("   ❌ No submit button")
        return None
    
    await submit_btn.click()
    print("   ✓ Submitted\n")
    
    # Wait for verification
    print("[3] ⏳ Waiting for verification result...")
    print("   (Checking every 10 seconds for up to 5 minutes)\n")
    
    max_wait = 300  # 5 minutes
    check_interval = 10
    elapsed = 0
    
    while elapsed < max_wait:
        await asyncio.sleep(check_interval)
        elapsed += check_interval
        
        try:
            text = await page.inner_text('body')
            
            # Success
            if any(word in text.lower() for word in ['success', 'verified', 'approved', 'congratulations', 'eligible', 'confirmed']):
                print(f"\n{'=' * 70}")
                print("✅ VERIFICATION SUCCESSFUL!")
                print("=" * 70)
                
                await page.screenshot(path=str(output_dir / f"SUCCESS_attempt{attempt}.png"))
                
                # Try to extract code
                import re
                for pattern in [r'code[:\s]+([A-Z0-9-]{6,})', r'promo[:\s]+([A-Z0-9-]{6,})', r'discount[:\s]+([A-Z0-9-]{6,})']:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        code = match.group(1)
                        print(f"\n🎁 DISCOUNT CODE: {code}\n")
                        
                        # Save
                        Path(output_dir / 'DISCOUNT_CODE.txt').write_text(
                            f"Code: {code}\nDate: {datetime.now()}\nAttempt: {attempt}\n"
                        )
                        break
                
                return 'success'
            
            # Failure
            if any(word in text.lower() for word in ['reject', 'denied', 'unable to verify', 'not official', 'not on the list', 'error', 'limit exceeded']):
                print(f"\n{'=' * 70}")
                print(f"❌ VERIFICATION FAILED (Attempt {attempt})")
                print("=" * 70)
                
                await page.screenshot(path=str(output_dir / f"FAILED_attempt{attempt}.png"))
                
                # Save error details
                Path(output_dir / f'error_attempt{attempt}.txt').write_text(
                    f"Failed at: {datetime.now()}\nAttempt: {attempt}\nReason:\n{text[:1000]}\n"
                )
                
                # Check if limit exceeded (cannot retry)
                if 'limit exceeded' in text.lower():
                    print("\n⛔ Document review limit exceeded - cannot retry with this verification ID\n")
                    return 'limit_exceeded'
                
                return 'failed'
            
            # Still reviewing
            if elapsed % 30 == 0:  # Print every 30 seconds
                print(f"   ⏱️  {elapsed}s - Still reviewing...")
        
        except Exception as e:
            print(f"   Error checking status: {e}")
    
    # Timeout
    print(f"\n⏱️  Timeout after {max_wait}s")
    await page.screenshot(path=str(output_dir / f"TIMEOUT_attempt{attempt}.png"))
    return 'timeout'

async def main():
    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = os.getenv('SHEERID_URL', DEFAULT_URL)
    
    print("=" * 70)
    print("UNIFIED VERIFICATION FLOW - STUDENT ID CARD")
    print("=" * 70)
    print(f"\n🔗 URL: {url}")
    print(f"👤 Student: {STUDENT_DATA['first_name']} {STUDENT_DATA['last_name']}")
    print(f"🆔 ID: {STUDENT_DATA['student_id']}")
    print(f"🏫 University: {STUDENT_DATA['university']}")
    print(f"📇 Document Type: Student ID Card with Expiration Date\n")
    
    browser = None
    
    try:
        # Initialize browser
        print("[Init] Launching browser...")
        browser = StealthBrowser(headless=False)
        await browser.initialize()
        page = browser.page
        print("   ✓ Ready\n")
        
        # Navigate
        print("[Navigate] Loading SheerID page...")
        await page.goto(url, wait_until='load', timeout=30000)
        await asyncio.sleep(3)
        print("   ✓ Loaded\n")
        
        # Fill form if needed
        form_result = await fill_form_if_needed(page)
        if not form_result:
            print("❌ Failed to process form")
            return 1
        
        # Retry loop with new documents
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            # Generate fresh Student ID document for each attempt
            document_path = await generate_student_id_document()
            
            # Upload and wait
            result = await upload_document_and_wait(page, document_path, attempt)
            
            if result == 'success':
                print("\n🎉 Verification completed successfully!\n")
                return 0
            
            elif result == 'limit_exceeded':
                print("\n⛔ Cannot retry - verification limit reached\n")
                return 1
            
            elif result == 'failed' and attempt < max_attempts:
                print(f"\n🔄 Retrying with new document (Attempt {attempt + 1}/{max_attempts})...\n")
                await asyncio.sleep(5)
                continue
            
            elif result == 'timeout':
                print(f"\n⏱️  Verification timeout on attempt {attempt}\n")
                if attempt < max_attempts:
                    print(f"🔄 Retrying (Attempt {attempt + 1}/{max_attempts})...\n")
                    continue
                else:
                    print("❌ Max attempts reached\n")
                    return 1
            
            else:
                print(f"\n❌ Verification failed after {attempt} attempts\n")
                return 1
        
        print("\n❌ Max retry attempts reached\n")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        if browser and browser.page:
            try:
                await browser.page.screenshot(path="output/exception_error.png")
            except:
                pass
        
        return 1
    
    finally:
        if browser:
            print("\n⏸️  Browser will stay open for inspection...")
            print("Press Ctrl+C to close\n")
            try:
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                pass
            await browser.close()

if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python unified_flow.py [URL]")
        print("\nExamples:")
        print("  python unified_flow.py")
        print("  python unified_flow.py https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=YOUR_ID")
        print("\nDocument Type: Student ID Card with Expiration Date")
        print("This is SheerID's first suggested acceptable document type.")
        sys.exit(0)
    
    sys.exit(asyncio.run(main()))
