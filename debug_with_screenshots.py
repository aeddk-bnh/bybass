"""
Debug script with browser visible and screenshots at each step
"""

import asyncio
from datetime import datetime
from core.browser import StealthBrowser


async def main():
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    print("="*70)
    print("DEBUG MODE - Browser Visible + Screenshots")
    print("="*70)
    print(f"URL: {url}\n")
    
    # Test data - Stanford University
    first_name = "John"
    last_name = "Smith"
    email = "john.smith@stanford.edu"
    birth_day = 15
    birth_month = 6
    birth_year = 2000
    
    print("Test Identity:")
    print(f"  Name: {first_name} {last_name}")
    print(f"  Email: {email}")
    print(f"  Birth Date: {birth_month}/{birth_day}/{birth_year}")
    print()
    
    browser = None
    
    try:
        print("[STEP 1] Initializing browser (VISIBLE mode)...")
        browser = StealthBrowser(headless=False)  # VISIBLE BROWSER
        await browser.initialize()
        print("  ✓ Browser initialized\n")
        
        print("[STEP 2] Navigating to URL...")
        await browser.navigate(url)
        await asyncio.sleep(5)  # Wait for page load
        await browser.screenshot('output/debug_01_initial_page.png')
        print("  ✓ Page loaded")
        print("  📸 Screenshot: output/debug_01_initial_page.png\n")
        
        print("[STEP 3] Inspecting form structure...")
        # Get all input fields
        page_html = await browser.page.content()
        
        # Save page HTML for analysis
        with open('output/debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_html)
        print("  ✓ Page source saved: output/debug_page_source.html")
        
        # Try to find all input fields
        inputs = await browser.page.query_selector_all('input')
        print(f"  ✓ Found {len(inputs)} input fields")
        
        selects = await browser.page.query_selector_all('select')
        print(f"  ✓ Found {len(selects)} select fields")
        
        buttons = await browser.page.query_selector_all('button')
        print(f"  ✓ Found {len(buttons)} buttons\n")
        
        print("[STEP 4] Filling firstName...")
        try:
            await browser.page.fill('#sid-first-name', first_name)
            await asyncio.sleep(1)
            await browser.screenshot('output/debug_02_after_firstname.png')
            print("  ✓ First name filled")
            print("  📸 Screenshot: output/debug_02_after_firstname.png\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
        
        print("[STEP 5] Filling lastName...")
        try:
            await browser.page.fill('#sid-last-name', last_name)
            await asyncio.sleep(1)
            await browser.screenshot('output/debug_03_after_lastname.png')
            print("  ✓ Last name filled")
            print("  📸 Screenshot: output/debug_03_after_lastname.png\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
        
        print("[STEP 6] Filling email...")
        try:
            await browser.page.fill('#sid-email', email)
            await asyncio.sleep(1)
            await browser.screenshot('output/debug_04_after_email.png')
            print("  ✓ Email filled")
            print("  📸 Screenshot: output/debug_04_after_email.png\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
        
        print("[STEP 7] Analyzing birthdate fields...")
        print("  Trying to find birthdate elements...\n")
        
        # Try different birthdate selectors
        birthdate_selectors = [
            '#sid-birthdate',
            '#sid-birthdate-day',
            '#sid-birthdate-month',
            '#sid-birthdate-year',
            'input[name="birthdate"]',
            'input[placeholder*="birth"]',
            'input[placeholder*="Birth"]',
            'select[name*="birth"]',
        ]
        
        found_selectors = []
        for selector in birthdate_selectors:
            try:
                element = await browser.page.query_selector(selector)
                if element:
                    # Get element info
                    tag_name = await element.evaluate('el => el.tagName')
                    element_type = await element.evaluate('el => el.type')
                    element_name = await element.evaluate('el => el.name')
                    element_id = await element.evaluate('el => el.id')
                    element_placeholder = await element.evaluate('el => el.placeholder')
                    
                    info = f"    ✓ Found: {selector}"
                    info += f"\n      Tag: {tag_name}, Type: {element_type}"
                    info += f"\n      ID: {element_id}, Name: {element_name}"
                    info += f"\n      Placeholder: {element_placeholder}"
                    print(info)
                    
                    found_selectors.append({
                        'selector': selector,
                        'tag': tag_name,
                        'type': element_type,
                        'id': element_id,
                        'name': element_name
                    })
            except:
                pass
        
        print(f"\n  Total birthdate-related fields found: {len(found_selectors)}\n")
        
        print("[STEP 8] Attempting to fill birthdate...")
        
        # Strategy 1: Try single date input
        try:
            print("  Strategy 1: Single date field (#sid-birthdate)")
            await browser.page.fill('#sid-birthdate', f'{birth_month}/{birth_day}/{birth_year}')
            await asyncio.sleep(1)
            await browser.screenshot('output/debug_05_birthdate_attempt1.png')
            print("    ✓ Filled single date field")
            print("    📸 Screenshot: output/debug_05_birthdate_attempt1.png\n")
        except Exception as e:
            print(f"    ✗ Failed: {e}\n")
            
            # Strategy 2: Try separate fields
            try:
                print("  Strategy 2: Separate day/month/year fields")
                
                # Day
                try:
                    await browser.page.fill('#sid-birthdate-day', str(birth_day))
                    print(f"    ✓ Day filled: {birth_day}")
                except Exception as e:
                    print(f"    ✗ Day failed: {e}")
                
                await asyncio.sleep(0.5)
                
                # Month - try as select dropdown first
                try:
                    await browser.page.select_option('#sid-birthdate-month', str(birth_month))
                    print(f"    ✓ Month selected (dropdown): {birth_month}")
                except:
                    # Try as input
                    try:
                        await browser.page.fill('#sid-birthdate-month', str(birth_month))
                        print(f"    ✓ Month filled (input): {birth_month}")
                    except Exception as e:
                        print(f"    ✗ Month failed: {e}")
                
                await asyncio.sleep(0.5)
                
                # Year
                try:
                    await browser.page.fill('#sid-birthdate-year', str(birth_year))
                    print(f"    ✓ Year filled: {birth_year}")
                except Exception as e:
                    print(f"    ✗ Year failed: {e}")
                
                await asyncio.sleep(1)
                await browser.screenshot('output/debug_06_birthdate_attempt2.png')
                print("    📸 Screenshot: output/debug_06_birthdate_attempt2.png\n")
                
            except Exception as e:
                print(f"    ✗ Strategy 2 failed: {e}\n")
        
        print("[STEP 9] Final form state before submit...")
        await browser.screenshot('output/debug_07_before_submit.png')
        print("  📸 Screenshot: output/debug_07_before_submit.png\n")
        
        print("[STEP 10] Locating submit button...")
        submit_selectors = [
            '#sid-submit-wrapper__collect-info',
            'button[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Verify")',
            'button:has-text("Continue")',
        ]
        
        submit_found = False
        for selector in submit_selectors:
            try:
                button = await browser.page.query_selector(selector)
                if button:
                    button_text = await button.inner_text()
                    print(f"  ✓ Found submit button: {selector}")
                    print(f"    Text: {button_text}")
                    submit_found = True
                    break
            except:
                pass
        
        if not submit_found:
            print("  ✗ Submit button not found\n")
        
        print("\n" + "="*70)
        print("DEBUG SESSION PAUSED")
        print("="*70)
        print("\nBrowser will stay open for manual inspection.")
        print("Check the screenshots in output/ folder.")
        print("\nPress Ctrl+C to close browser and exit.\n")
        print("Files created:")
        print("  - output/debug_01_initial_page.png")
        print("  - output/debug_02_after_firstname.png")
        print("  - output/debug_03_after_lastname.png")
        print("  - output/debug_04_after_email.png")
        print("  - output/debug_05_birthdate_attempt1.png (if applicable)")
        print("  - output/debug_06_birthdate_attempt2.png (if applicable)")
        print("  - output/debug_07_before_submit.png")
        print("  - output/debug_page_source.html")
        print("="*70)
        
        # Keep browser open for manual inspection
        await asyncio.sleep(300)  # 5 minutes
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser:
            print("\nClosing browser...")
            try:
                await browser.close()
            except:
                pass
        print("Done.")


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
