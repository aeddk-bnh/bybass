#!/usr/bin/env python3
"""
Quick check of last verification result
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Loading page...")
        await page.goto(url, wait_until='load')
        await asyncio.sleep(3)
        
        # Get page text
        text = await page.inner_text('body')
        
        print("\n" + "=" * 70)
        print("PAGE CONTENT")
        print("=" * 70)
        print(text)
        print("=" * 70)
        
        # Save to file
        output = Path("output/page_text.txt")
        output.write_text(text, encoding='utf-8')
        print(f"\nSaved to: {output}")
        
        # Take screenshot
        await page.screenshot(path='output/current_state.png')
        print("Screenshot: output/current_state.png")
        
        # Keep open for inspection
        print("\nBrowser will stay open for 30 seconds...")
        try:
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            pass
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
