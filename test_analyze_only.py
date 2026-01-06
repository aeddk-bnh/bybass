"""
Simple test - just analyze the SheerID form
"""

import asyncio
from core.analyzer import SheerIDAnalyzer


async def main():
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    print("="*70)
    print("ANALYZING SHEERID FORM")
    print("="*70)
    print(f"URL: {url}\n")
    
    analyzer = SheerIDAnalyzer()
    
    try:
        print("Initializing browser...")
        await analyzer.initialize(headless=True)
        print("OK - Browser initialized\n")
        
        print("Loading page (this may take 30-60 seconds)...")
        analysis = await analyzer.analyze_url(url)
        
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        print(f"Verification Type: {analysis['verification_type']}")
        print(f"University: {analysis.get('university', 'Not detected')}")
        print(f"Organization: {analysis.get('organization', 'Not detected')}")
        print(f"Has SSO: {analysis['has_sso']}")
        print(f"Has Upload: {analysis['has_upload']}")
        print(f"\nRequired Fields:")
        for field_name in analysis.get('required_fields', []):
            print(f"  - {field_name}")
        print(f"\nForm Selectors:")
        for field, selector in analysis.get('form_selectors', {}).items():
            print(f"  {field}: {selector}")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await analyzer.close()
            print("\nBrowser closed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
