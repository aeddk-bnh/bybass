"""
SheerID Research Application - Main Orchestration
Complete end-to-end workflow for authentication system research

This application is for SECURITY RESEARCH PURPOSES ONLY.
"""

import asyncio
import argparse
import os
import sys
from typing import Dict, Optional
import logging

# Import core modules
from core.crawler import TemplateCrawler
from core.browser import StealthBrowser
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SheerIDResearchApp:
    """
    Main application orchestrator for SheerID authentication research
    Coordinates all modules to execute the complete workflow
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize modules
        self.crawler = TemplateCrawler()
        self.renderer = DocumentRenderer()
        self.processor = ImageProcessor()
        self.spoofing = MetadataSpoofing()
        self.data_generator = DocumentDataGenerator()
        
        # Browser will be initialized when needed
        self.browser = None
        
    async def collect_templates(self, university: str) -> bool:
        """
        Step 1: Collect document templates for university
        
        Args:
            university: University name
            
        Returns:
            True if templates collected successfully
        """
        logger.info(f"[Step 1] Collecting templates for {university}")
        
        universities = [{'name': university, 'domain': f'{university.lower().replace(" ", "")}.edu'}]
        results = self.crawler.collect_templates(universities)
        
        if results.get(university):
            logger.info(f"Collected {len(results[university])} templates")
            return True
        else:
            logger.warning("No templates found, will use default templates")
            return False
    
    async def generate_document(self, template_name: str, student_data: Dict) -> str:
        """
        Step 2: Generate synthetic document from template
        
        Args:
            template_name: Template file path (e.g., 'stanford/bill.html')
            student_data: Student information dictionary
            
        Returns:
            Path to generated raw image
        """
        logger.info("[Step 2] Generating document from template")
        
        # Render template with data
        image_path = await self.renderer.render_and_capture(
            template_name=template_name,
            data=student_data
        )
        
        logger.info(f"Generated document: {image_path}")
        return image_path
    
    def process_document(self, image_path: str, intensity: str = 'medium') -> str:
        """
        Step 3: Apply realistic photo effects
        
        Args:
            image_path: Path to raw document image
            intensity: Processing intensity ('light', 'medium', 'heavy')
            
        Returns:
            Path to processed image
        """
        logger.info("[Step 3] Applying realistic photo processing")
        
        # Generate output path
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_realistic.jpg"
        
        # Process image
        processed_path = self.processor.process_realistic_photo(
            image_path=image_path,
            output_path=output_path,
            intensity=intensity
        )
        
        logger.info(f"Processed document: {processed_path}")
        return processed_path
    
    def spoof_metadata(self, image_path: str, device: str = 'iphone_13_pro') -> bool:
        """
        Step 4: Spoof EXIF metadata to simulate mobile capture
        
        Args:
            image_path: Path to image file
            device: Device profile to simulate
            
        Returns:
            True if successful
        """
        logger.info(f"[Step 4] Spoofing metadata to simulate {device}")
        
        success = self.spoofing.spoof_realistic_photo(image_path, device)
        
        if success:
            logger.info("Metadata spoofing completed")
        else:
            logger.warning("Metadata spoofing failed (ExifTool may not be installed)")
        
        return success
    
    async def automate_verification(self, sheerid_url: str, form_data: Dict, 
                                   document_path: str) -> Optional[str]:
        """
        Step 5: Automate browser interaction and document submission
        
        Args:
            sheerid_url: SheerID verification URL
            form_data: Form field data (selectors mapped to values)
            document_path: Path to prepared document
            
        Returns:
            Discount code if successful, None otherwise
        """
        logger.info("[Step 5] Starting browser automation")
        
        # Initialize browser
        self.browser = StealthBrowser(
            headless=self.config.get('headless', False),
            proxy=self.config.get('proxy')
        )
        
        try:
            await self.browser.initialize()
            
            # Navigate to verification page
            await self.browser.navigate(sheerid_url)
            
            # Fill form
            await self.browser.fill_form(form_data)
            
            # Enable SSO interception
            await self.browser.intercept_sso_requests()
            
            # Upload document
            await self.browser.upload_document(document_path)
            
            # Wait for approval
            approved = await self.browser.wait_for_approval(
                approval_selector='.approval-message, .success-message',
                timeout=120000
            )
            
            if approved:
                # Extract discount code
                code = await self.browser.extract_discount_code(
                    code_selector='.discount-code, .promo-code'
                )
                logger.info(f"Successfully obtained code: {code}")
                return code
            else:
                logger.warning("Verification not approved within timeout")
                return None
                
        except Exception as e:
            logger.error(f"Browser automation error: {e}")
            return None
        finally:
            if self.browser:
                await self.browser.close()
    
    async def run_full_workflow(self, university: str, student_name: str, 
                               student_id: str, sheerid_url: str, 
                               template_name: str = None) -> Dict:
        """
        Execute complete end-to-end workflow
        
        Args:
            university: University name
            student_name: Student full name
            student_id: Student ID number
            sheerid_url: SheerID verification URL
            template_name: Optional specific template to use
            
        Returns:
            Dictionary with results and generated files
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL SHEERID RESEARCH WORKFLOW")
        logger.info("=" * 60)
        
        results = {
            'success': False,
            'university': university,
            'student_name': student_name,
            'files': {},
            'code': None
        }
        
        try:
            # Step 1: Collect templates (optional, use existing if available)
            if self.config.get('collect_templates', False):
                await self.collect_templates(university)
            
            # Step 2: Generate document
            if not template_name:
                # Auto-detect template based on university
                if 'stanford' in university.lower():
                    template_name = 'stanford/bill.html'
                elif 'bach khoa' in university.lower() or 'hust' in university.lower():
                    template_name = 'bachkhoa_hanoi/enrollment.html'
                else:
                    template_name = 'stanford/bill.html'  # Default
            
            # Generate appropriate data
            if 'bill' in template_name:
                student_data = self.data_generator.generate_tuition_bill_data(
                    student_name=student_name,
                    student_id=student_id,
                    university=university
                )
            else:
                student_data = self.data_generator.generate_enrollment_verification_data(
                    student_name=student_name,
                    student_id=student_id,
                    university=university
                )
            
            raw_image = await self.generate_document(template_name, student_data)
            results['files']['raw_image'] = raw_image
            
            # Step 3: Process image
            processed_image = self.process_document(
                raw_image, 
                intensity=self.config.get('processing_intensity', 'medium')
            )
            results['files']['processed_image'] = processed_image
            
            # Step 4: Spoof metadata
            device = self.config.get('device_profile', 'iphone_13_pro')
            self.spoof_metadata(processed_image, device)
            results['files']['final_document'] = processed_image
            
            # Step 5: Browser automation (if URL provided)
            if sheerid_url and sheerid_url != 'skip':
                # Prepare form data
                email_domain = university.lower().replace(' ', '').replace('university', '') + '.edu'
                form_data = {
                    '#firstName': student_name.split()[0],
                    '#lastName': ' '.join(student_name.split()[1:]),
                    '#email': f"{student_name.lower().replace(' ', '.')}@{email_domain}",
                    '#studentId': student_id
                }
                
                code = await self.automate_verification(
                    sheerid_url=sheerid_url,
                    form_data=form_data,
                    document_path=processed_image
                )
                
                results['code'] = code
                results['success'] = code is not None
            else:
                logger.info("Skipping browser automation (no URL provided)")
                results['success'] = True
            
            logger.info("=" * 60)
            logger.info("WORKFLOW COMPLETED")
            logger.info(f"Success: {results['success']}")
            logger.info(f"Final document: {results['files']['final_document']}")
            if results['code']:
                logger.info(f"Discount code: {results['code']}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            results['error'] = str(e)
        
        return results


async def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='SheerID Research Application - Security Research Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate document only (no browser automation)
  python main.py --university "Stanford University" --name "John Doe" --id "20240001"
  
  # Full workflow with browser automation
  python main.py --university "Stanford University" --name "John Doe" --id "20240001" \\
                 --url "https://verify.sheerid.com/..." --headless
  
  # Use specific template and device
  python main.py --university "HUST" --name "Nguyen Van A" --id "20210001" \\
                 --template "bachkhoa_hanoi/enrollment.html" --device "samsung_s23"
        """
    )
    
    # Required arguments
    parser.add_argument('--university', '-u', required=True,
                       help='University name (e.g., "Stanford University")')
    parser.add_argument('--name', '-n', required=True,
                       help='Student full name')
    parser.add_argument('--id', '-i', required=True,
                       help='Student ID number')
    
    # Optional arguments
    parser.add_argument('--url', default='skip',
                       help='SheerID verification URL (skip to generate document only)')
    parser.add_argument('--template', '-t',
                       help='Specific template to use (e.g., stanford/bill.html)')
    parser.add_argument('--device', '-d', default='iphone_13_pro',
                       help='Device profile for metadata spoofing')
    parser.add_argument('--intensity', default='medium',
                       choices=['light', 'medium', 'heavy'],
                       help='Image processing intensity')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--collect-templates', action='store_true',
                       help='Collect new templates via crawling')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'headless': args.headless,
        'device_profile': args.device,
        'processing_intensity': args.intensity,
        'collect_templates': args.collect_templates
    }
    
    # Initialize and run application
    app = SheerIDResearchApp(config)
    
    results = await app.run_full_workflow(
        university=args.university,
        student_name=args.name,
        student_id=args.id,
        sheerid_url=args.url,
        template_name=args.template
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("EXECUTION RESULTS")
    print("=" * 60)
    print(f"Success: {results['success']}")
    print(f"University: {results['university']}")
    print(f"Student: {results['student_name']}")
    print(f"\nGenerated files:")
    for file_type, path in results['files'].items():
        print(f"  {file_type}: {path}")
    
    if results.get('code'):
        print(f"\n🎉 Discount Code: {results['code']}")
    
    if results.get('error'):
        print(f"\n❌ Error: {results['error']}")
    
    print("=" * 60)
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
