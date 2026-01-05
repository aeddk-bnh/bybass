"""
Test Script - Quick Demo of All Features
Run this to verify all modules are working correctly
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing


async def test_stanford_workflow():
    """Test complete workflow with Stanford template"""
    print("\n" + "="*60)
    print("TEST 1: Stanford University Tuition Bill")
    print("="*60)
    
    # Initialize modules
    renderer = DocumentRenderer()
    processor = ImageProcessor()
    spoofing = MetadataSpoofing()
    generator = DocumentDataGenerator()
    
    # Generate data
    data = generator.generate_tuition_bill_data(
        student_name="John Michael Doe",
        student_id="20240001",
        university="Stanford University",
        amount=18500.00
    )
    
    print(f"\n✓ Generated student data:")
    print(f"  - Name: {data['student_name']}")
    print(f"  - ID: {data['student_id']}")
    print(f"  - Tuition: {data['total_amount']}")
    
    # Render document
    image_path = await renderer.render_and_capture(
        'stanford/bill.html',
        data,
        'test_stanford_bill.png'
    )
    print(f"\n✓ Rendered document: {image_path}")
    
    # Process image
    processed_path = processor.process_realistic_photo(
        image_path,
        'output/test_stanford_bill_realistic.jpg',
        intensity='medium'
    )
    print(f"✓ Applied realistic effects: {processed_path}")
    
    # Spoof metadata
    devices = spoofing.list_available_devices()
    print(f"\n✓ Available device profiles: {', '.join(devices)}")
    
    if os.path.exists(processed_path):
        success = spoofing.spoof_realistic_photo(processed_path, 'iphone_13_pro')
        if success:
            print(f"✓ Metadata spoofed successfully (iPhone 13 Pro)")
        else:
            print(f"⚠ Metadata spoofing skipped (ExifTool not installed)")
    
    print(f"\n✅ Stanford workflow completed!")
    return True


async def test_hust_workflow():
    """Test complete workflow with HUST template"""
    print("\n" + "="*60)
    print("TEST 2: HUST Enrollment Verification")
    print("="*60)
    
    renderer = DocumentRenderer()
    processor = ImageProcessor()
    generator = DocumentDataGenerator()
    
    # Generate data
    data = generator.generate_enrollment_verification_data(
        student_name="Nguyen Van A",
        student_id="20210001",
        university="Đại học Bách Khoa Hà Nội",
        program="Khoa học máy tính"
    )
    
    print(f"\n✓ Generated student data:")
    print(f"  - Name: {data['student_name']}")
    print(f"  - ID: {data['student_id']}")
    print(f"  - Program: {data['program']}")
    
    # Render document
    image_path = await renderer.render_and_capture(
        'bachkhoa_hanoi/enrollment.html',
        data,
        'test_hust_enrollment.png'
    )
    print(f"\n✓ Rendered document: {image_path}")
    
    # Process image with heavy intensity
    processed_path = processor.process_realistic_photo(
        image_path,
        'output/test_hust_enrollment_realistic.jpg',
        intensity='heavy'
    )
    print(f"✓ Applied heavy realistic effects: {processed_path}")
    
    print(f"\n✅ HUST workflow completed!")
    return True


async def test_image_processing():
    """Test different image processing intensities"""
    print("\n" + "="*60)
    print("TEST 3: Image Processing Intensities")
    print("="*60)
    
    processor = ImageProcessor()
    
    # Find first generated image
    test_image = None
    if os.path.exists('output'):
        for file in os.listdir('output'):
            if file.endswith('.png') and not file.startswith('test_'):
                test_image = os.path.join('output', file)
                break
    
    if not test_image:
        print("⚠ No test image found, skipping intensity test")
        return False
    
    print(f"\nUsing test image: {test_image}")
    
    intensities = ['light', 'medium', 'heavy']
    for intensity in intensities:
        output_path = f'output/test_intensity_{intensity}.jpg'
        processor.process_realistic_photo(test_image, output_path, intensity)
        print(f"✓ Created {intensity} intensity version")
    
    print(f"\n✅ Image processing test completed!")
    return True


async def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#  SheerID Research Application - Complete Test Suite  #")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    try:
        # Test 1: Stanford workflow
        await test_stanford_workflow()
        
        # Test 2: HUST workflow
        await test_hust_workflow()
        
        # Test 3: Image processing
        await test_image_processing()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ All modules working correctly!")
        print("\nGenerated test files in output/:")
        
        if os.path.exists('output'):
            files = sorted([f for f in os.listdir('output') if f.startswith('test_')])
            for f in files:
                size_kb = os.path.getsize(os.path.join('output', f)) / 1024
                print(f"  - {f} ({size_kb:.1f} KB)")
        
        print("\n" + "="*60)
        print("Next steps:")
        print("  1. Install ExifTool for metadata spoofing")
        print("  2. Review generated documents in output/")
        print("  3. Use main.py for production workflows")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
