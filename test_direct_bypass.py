"""
Direct bypass test with US universities
Based on analysis: Student verification for Google One
- Has SSO option
- Form fields: firstName, lastName, email, birthDate
"""

import asyncio
import random
from datetime import datetime
from core.browser import StealthBrowser
from core.template_generator import UniversityDatabase


async def main():
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    print("="*70)
    print("DIRECT BYPASS TEST - US UNIVERSITIES")
    print("="*70)
    print(f"URL: {url}\n")
    
    # Get US universities
    all_unis = UniversityDatabase.get_all_universities()
    us_unis = [u for u in all_unis if u['country'] == 'USA']
    
    print(f"Will try {len(us_unis)} US universities:")
    for i, uni in enumerate(us_unis, 1):
        print(f"  {i}. {uni['name']} ({uni['domain']})")
    print()
    
    # Try each university
    for attempt, university in enumerate(us_unis, 1):
        print("="*70)
        print(f"ATTEMPT {attempt}/{len(us_unis)}: {university['name']}")
        print("="*70)
        
        # Generate student data
        first_names = ['John', 'Michael', 'David', 'James', 'Robert', 'William']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Davis']
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate student ID
        year = random.randint(2020, 2024)
        num = random.randint(1, 9999)
        try:
            student_id = university['id_format'].format(year=year, num=num)
        except:
            student_id = f"{year}{num:05d}"
        
        # Generate email with university domain
        email = f"{first_name.lower()}.{last_name.lower()}@{university['domain']}"
        
        # Generate birthdate
        birth_year = random.randint(1995, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        print(f"\nGenerated Identity:")
        print(f"  Name: {first_name} {last_name}")
        print(f"  Email: {email}")
        print(f"  Student ID: {student_id}")
        print(f"  Birth Date: {birth_month}/{birth_day}/{birth_year}")
        print()
        
        # Try to submit
        browser = None
        try:
            print("Initializing browser...")
            browser = StealthBrowser(headless=True)
            await browser.initialize()
            
            print("Navigating to URL...")
            await browser.navigate(url)
            await asyncio.sleep(3)
            
            print("Filling form...")
            # Fill form fields (based on analysis)
            try:
                await browser.page.fill('#sid-first-name', first_name)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  Warning: Could not fill first name: {e}")
            
            try:
                await browser.page.fill('#sid-last-name', last_name)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  Warning: Could not fill last name: {e}")
            
            try:
                await browser.page.fill('#sid-email', email)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  Warning: Could not fill email: {e}")
            
            # Birth date - try different selectors
            try:
                # Try single field first
                await browser.page.fill('#sid-birthdate', f"{birth_month}/{birth_day}/{birth_year}")
                await asyncio.sleep(0.5)
            except:
                # Try separate fields
                try:
                    await browser.page.fill('#sid-birthdate-day', str(birth_day))
                    await asyncio.sleep(0.3)
                except:
                    pass
                
                try:
                    await browser.page.select_option('#sid-birthdate-month', str(birth_month))
                    await asyncio.sleep(0.3)
                except:
                    pass
                
                try:
                    await browser.page.fill('#sid-birthdate-year', str(birth_year))
                    await asyncio.sleep(0.5)
                except:
                    pass
            
            print("Submitting...")
            # Click submit
            await browser.page.click('#sid-submit-wrapper__collect-info')
            await asyncio.sleep(5)
            
            # Check result
            print("Checking result...")
            page_content = await browser.page.content()
            page_text = page_content.lower()
            
            # Check for success indicators
            if 'success' in page_text or 'verified' in page_text or 'approved' in page_text:
                print("\n" + "="*70)
                print("*** SUCCESS! ***")
                print("="*70)
                print(f"University: {university['name']}")
                print(f"Email: {email}")
                
                # Try to extract code
                try:
                    import re
                    patterns = [
                        r'code[:\s]+([A-Z0-9]{6,})',
                        r'discount[:\s]+([A-Z0-9]{6,})',
                        r'\b([A-Z0-9]{8,12})\b'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, page_content, re.IGNORECASE)
                        if match:
                            print(f"Code: {match.group(1)}")
                            break
                except:
                    pass
                
                # Save screenshot
                await browser.screenshot(f'output/success_{university["key"]}.png')
                print(f"Screenshot saved: output/success_{university['key']}.png")
                print("="*70)
                
                await browser.close()
                return 0
                
            elif 'error' in page_text or 'invalid' in page_text:
                print(f"Failed: Form error or invalid data")
                await browser.screenshot(f'output/failed_{university["key"]}.png')
                
            else:
                print(f"Status unclear - saving screenshot")
                await browser.screenshot(f'output/attempt_{university["key"]}.png')
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass
        
        print(f"\nWaiting 3 seconds before next attempt...")
        await asyncio.sleep(3)
    
    print("\n" + "="*70)
    print("ALL ATTEMPTS COMPLETED")
    print("Check output/ folder for screenshots")
    print("="*70)
    
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
