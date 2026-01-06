"""
Test auto-bypass with US universities only
"""

import asyncio
import sys
import logging
from core.template_generator import TemplateGenerator, UniversityDatabase
from auto_bypass import AutoBypass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # SheerID URL
    url = "https://services.sheerid.com/verify/67c8c14f5f17a83b745e3f82/?verificationId=695c84ea46509f39b613b1a3"
    
    print("="*70)
    print("US UNIVERSITIES ONLY - AUTO BYPASS TEST")
    print("="*70)
    print(f"\nTarget URL: {url}")
    print()
    
    # Filter only US universities
    all_unis = UniversityDatabase.get_all_universities()
    us_unis = [u for u in all_unis if u['country'] == 'USA']
    
    print(f"US Universities to try: {len(us_unis)}")
    for uni in us_unis:
        print(f"  • {uni['name']}")
    print()
    
    # Generate US templates if not exist
    print("Generating US university templates...")
    gen = TemplateGenerator()
    for uni in us_unis:
        gen.create_template(uni['key'])
    print("✓ Templates ready\n")
    
    # Run bypass with multi-university
    print("="*70)
    print("Starting auto-bypass with US universities...")
    print("="*70)
    print()
    
    bypass = AutoBypass(headless=True)  # Headless mode
    
    # Enable multi-university mode with US filter
    from core.strategies import StrategyManager
    bypass.strategy_manager = StrategyManager(enable_multi_university=True, country_filter='USA')
    
    try:
        results = await bypass.bypass(url)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Print results
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Success: {'YES' if results['success'] else 'NO'}")
    
    if results.get('strategy_used'):
        print(f"\nWinning Strategy: {results['strategy_used']}")
        print(f"Total Attempts: {results.get('total_attempts', 0)}")
    
    if results['generated_data']:
        print(f"\nGenerated Identity:")
        print(f"  Name: {results['generated_data']['student_name']}")
        print(f"  ID: {results['generated_data']['student_id']}")
        print(f"  Email: {results['generated_data']['email']}")
        print(f"  University: {results['generated_data']['university']}")
    
    if results['files']:
        print(f"\nGenerated Files:")
        for file_type, path in results['files'].items():
            print(f"  {file_type}: {path}")
    
    if results['code']:
        print(f"\n*** Discount Code: {results['code']} ***")
    
    if results['error']:
        print(f"\nError: {results['error']}")
    
    print("="*70)
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
