#!/usr/bin/env python3
"""
Simple debug script - Load page, take screenshot, wait for manual inspection
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    print("=" * 70)
    print("SIMPLE DEBUG - Manual Inspection")
    print("=" * 70)
    
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    print(f"URL: {url}\n")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        print("[1] Launching browser (VISIBLE mode)...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Browser visible
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Hide webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            print("  ✓ Browser launched\n")
            
            print("[2] Loading page...")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            print("  ✓ Page loaded\n")
            
            print("[3] Taking screenshot...")
            await page.screenshot(path=str(output_dir / "page_loaded.png"))
            print(f"  ✓ Screenshot saved: output/page_loaded.png\n")
            
            print("[4] Saving HTML...")
            html = await page.content()
            (output_dir / "page_source.html").write_text(html, encoding='utf-8')
            print(f"  ✓ HTML saved: output/page_source.html\n")
            
            print("=" * 70)
            print("BROWSER IS OPEN - Inspect the form manually")
            print("Press Ctrl+C when done")
            print("=" * 70)
            
            # Wait indefinitely
            while True:
                await asyncio.sleep(60)
                
    except KeyboardInterrupt:
        print("\n\nClosing browser...")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDone.")
        sys.exit(0)
