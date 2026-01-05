"""
Quick test for retry system components
"""

import asyncio
import sys

async def test_strategies_import():
    """Test importing strategies module"""
    print("Testing strategies module import...")
    try:
        from core.strategies import (
            StrategyManager, 
            FormFillStrategy, 
            DocumentUploadStrategy,
            EmailDomainStrategy,
            SSOStrategy,
            StrategyResult
        )
        print("✓ All strategy classes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_strategy_manager_init():
    """Test strategy manager initialization"""
    print("\nTesting StrategyManager initialization...")
    try:
        from core.strategies import StrategyManager
        manager = StrategyManager()
        print(f"✓ StrategyManager initialized")
        print(f"✓ Registered {len(manager.strategies)} strategies:")
        for i, strategy in enumerate(manager.strategies, 1):
            print(f"  {i}. {strategy.name}: {strategy.description}")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

async def test_auto_bypass_import():
    """Test auto_bypass with retry system"""
    print("\nTesting auto_bypass.py with retry system...")
    try:
        from auto_bypass import AutoBypass
        bypass = AutoBypass(headless=True)
        print("✓ AutoBypass initialized successfully")
        print(f"✓ Strategy manager available: {hasattr(bypass, 'strategy_manager')}")
        if hasattr(bypass, 'strategy_manager'):
            print(f"✓ Strategy manager has {len(bypass.strategy_manager.strategies)} strategies")
        return True
    except Exception as e:
        print(f"✗ AutoBypass initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*70)
    print("🧪 RETRY SYSTEM TEST")
    print("="*70)
    print()
    
    results = []
    
    # Test 1: Import strategies
    results.append(await test_strategies_import())
    
    # Test 2: Strategy manager init
    results.append(await test_strategy_manager_init())
    
    # Test 3: Auto bypass with retry
    results.append(await test_auto_bypass_import())
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Retry system ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
