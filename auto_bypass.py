"""
Automatic SheerID Bypass System
Just provide the URL and let the system handle everything
"""

import asyncio
import sys
import random
from typing import Dict, Optional
from datetime import datetime
import logging

from core.analyzer import SheerIDAnalyzer
from core.browser import StealthBrowser
from core.document import DocumentRenderer, DocumentDataGenerator
from core.processor import ImageProcessor
from core.spoofing import MetadataSpoofing
from core.strategies import StrategyManager, StrategyResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoBypass:
    """
    Intelligent auto-bypass system that:
    1. Analyzes SheerID form
    2. Determines verification type
    3. Selects appropriate template
    4. Generates realistic data
    5. Creates document
    6. Submits and extracts result
    """
    
    # University templates mapping
    TEMPLATES = {
        'student': [
            ('stanford', 'Stanford University', 'stanford/bill.html', 'stanford.edu'),
            ('hust', 'Hanoi University of Science and Technology', 'bachkhoa_hanoi/enrollment.html', 'hust.edu.vn'),
        ]
    }
    
    # Common first/last names for generation
    FIRST_NAMES = ['John', 'Michael', 'David', 'James', 'Robert', 'William', 'Richard', 'Thomas']
    LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.analyzer = SheerIDAnalyzer()
        self.renderer = DocumentRenderer()
        self.processor = ImageProcessor()
        self.spoofing = MetadataSpoofing()
        self.data_generator = DocumentDataGenerator()
        self.strategy_manager = StrategyManager()
    
    async def bypass(self, sheerid_url: str, university_hint: Optional[str] = None) -> Dict:
        """
        Automatic bypass - just provide URL
        
        Args:
            sheerid_url: SheerID verification URL
            university_hint: Optional university name hint
            
        Returns:
            Dictionary with results including discount code
        """
        logger.info("="*70)
        logger.info("🚀 AUTO BYPASS SYSTEM STARTED")
        logger.info("="*70)
        
        results = {
            'success': False,
            'url': sheerid_url,
            'analysis': {},
            'generated_data': {},
            'files': {},
            'code': None,
            'error': None
        }
        
        try:
            # Step 1: Analyze form
            logger.info("\n[STEP 1/5] 🔍 Analyzing SheerID form...")
            await self.analyzer.initialize(headless=self.headless)
            analysis = await self.analyzer.analyze_url(sheerid_url)
            results['analysis'] = analysis
            
            logger.info(f"✓ Verification type: {analysis['verification_type']}")
            logger.info(f"✓ Has SSO: {analysis['has_sso']}")
            logger.info(f"✓ Has Upload: {analysis['has_upload']}")
            
            await self.analyzer.close()
            
            # Step 2: Select template and generate data
            logger.info("\n[STEP 2/5] 📝 Generating student data...")
            template_info = self._select_template(analysis, university_hint)
            student_data = self._generate_student_data(template_info)
            results['generated_data'] = student_data
            
            logger.info(f"✓ University: {student_data['university']}")
            logger.info(f"✓ Student: {student_data['student_name']} ({student_data['student_id']})")
            logger.info(f"✓ Email: {student_data['email']}")
            
            # Step 3: Generate document
            logger.info("\n[STEP 3/5] 🎨 Creating document...")
            doc_data = self._prepare_document_data(student_data, template_info)
            
            image_path = await self.renderer.render_and_capture(
                template_name=template_info['template'],
                data=doc_data
            )
            results['files']['raw_image'] = image_path
            logger.info(f"✓ Rendered: {image_path}")
            
            # Step 4: Process to look realistic
            logger.info("\n[STEP 4/5] 🖼️  Processing image...")
            processed_path = self.processor.process_realistic_photo(
                image_path=image_path,
                output_path=image_path.replace('.png', '_realistic.jpg'),
                intensity='medium'
            )
            results['files']['processed_image'] = processed_path
            
            # Spoof metadata
            device = random.choice(['iphone_13_pro', 'iphone_14', 'samsung_s23'])
            self.spoofing.spoof_realistic_photo(processed_path, device)
            results['files']['final_document'] = processed_path
            logger.info(f"✓ Processed: {processed_path}")
            logger.info(f"✓ Device: {device}")
            
            # Step 5: Submit to SheerID with intelligent retry
            logger.info("\n[STEP 5/5] 🌐 Submitting with intelligent retry system...")
            logger.info("🎯 System will try multiple strategies until success")
            
            # Prepare context for strategy manager
            browser = StealthBrowser(headless=self.headless)
            await browser.initialize()
            await browser.navigate(sheerid_url)
            await asyncio.sleep(3)
            
            context = {
                'browser': browser,
                'analysis': analysis,
                'student_data': student_data,
                'document_path': processed_path,
                'url': sheerid_url
            }
            
            # Execute with retry
            def on_attempt_callback(strategy_name: str, attempt_num: int):
                logger.info(f"💡 Trying: {strategy_name} (Attempt #{attempt_num})")
            
            try:
                strategy_result = await self.strategy_manager.execute_with_retry(
                    context=context,
                    on_attempt=on_attempt_callback
                )
                
                results['code'] = strategy_result.code
                results['success'] = strategy_result.success
                results['strategy_used'] = strategy_result.strategy_name
                results['total_attempts'] = strategy_result.attempts
                
            finally:
                await browser.close()
            
            # Final summary
            logger.info("\n" + "="*70)
            if results['success']:
                logger.info("✅ BYPASS SUCCESSFUL!")
                logger.info(f"🎉 Discount Code: {results['code']}")
                logger.info(f"📊 Strategy: {results.get('strategy_used', 'N/A')}")
                logger.info(f"🔢 Total Attempts: {results.get('total_attempts', 0)}")
            else:
                logger.info("⚠️  BYPASS COMPLETED (All strategies exhausted)")
                logger.info(f"🔢 Total Attempts: {results.get('total_attempts', 0)}")
                logger.info("💡 Manual verification may be required")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"\n❌ Error: {e}", exc_info=True)
            results['error'] = str(e)
        
        return results
    
    def _select_template(self, analysis: Dict, hint: Optional[str] = None) -> Dict:
        """Select appropriate template based on analysis"""
        verification_type = analysis['verification_type']
        
        if verification_type not in self.TEMPLATES:
            verification_type = 'student'  # Default
        
        templates = self.TEMPLATES[verification_type]
        
        # If hint provided, try to match
        if hint:
            for key, name, template, domain in templates:
                if hint.lower() in name.lower() or hint.lower() in key:
                    return {
                        'key': key,
                        'name': name,
                        'template': template,
                        'domain': domain
                    }
        
        # Otherwise, random selection
        key, name, template, domain = random.choice(templates)
        return {
            'key': key,
            'name': name,
            'template': template,
            'domain': domain
        }
    
    def _generate_student_data(self, template_info: Dict) -> Dict:
        """Generate realistic student data"""
        first_name = random.choice(self.FIRST_NAMES)
        last_name = random.choice(self.LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        # Generate student ID (realistic format)
        year = random.randint(2020, 2024)
        number = random.randint(1, 9999)
        student_id = f"{year}{number:04d}"
        
        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}@{template_info['domain']}"
        
        return {
            'university': template_info['name'],
            'template_key': template_info['key'],
            'first_name': first_name,
            'last_name': last_name,
            'student_name': full_name,
            'student_id': student_id,
            'email': email,
            'birth_date': f"{random.randint(1995, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        }
    
    def _prepare_document_data(self, student_data: Dict, template_info: Dict) -> Dict:
        """Prepare data for document template"""
        if 'bill' in template_info['template']:
            return self.data_generator.generate_tuition_bill_data(
                student_name=student_data['student_name'],
                student_id=student_data['student_id'],
                university=student_data['university']
            )
        else:
            return self.data_generator.generate_enrollment_verification_data(
                student_name=student_data['student_name'],
                student_id=student_data['student_id'],
                university=student_data['university']
            )
    
    async def _submit_verification(self, sheerid_url: str, analysis: Dict, 
                                   student_data: Dict, document_path: str) -> Optional[str]:
        """Submit verification to SheerID"""
        browser = StealthBrowser(headless=self.headless)
        
        try:
            await browser.initialize()
            await browser.navigate(sheerid_url)
            
            # Wait for form to load
            await asyncio.sleep(3)
            
            # Fill form based on detected selectors
            form_data = {}
            selectors = analysis['form_selectors']
            
            if 'firstName' in selectors:
                form_data[selectors['firstName']] = student_data['first_name']
            if 'lastName' in selectors:
                form_data[selectors['lastName']] = student_data['last_name']
            if 'email' in selectors:
                form_data[selectors['email']] = student_data['email']
            if 'birthDate' in selectors:
                form_data[selectors['birthDate']] = student_data['birth_date']
            
            logger.info("✓ Filling form fields...")
            await browser.fill_form(form_data)
            
            # Handle organization selection if available
            if 'organization' in selectors:
                try:
                    org_selector = selectors['organization']
                    # Try to select university from dropdown
                    await browser.page.select_option(org_selector, label=student_data['university'])
                    logger.info(f"✓ Selected organization: {student_data['university']}")
                except:
                    logger.warning("Could not auto-select organization")
            
            # Enable SSO interception if SSO detected
            if analysis['has_sso']:
                logger.info("✓ Enabling SSO bypass...")
                await browser.intercept_sso_requests()
            
            # Upload document if upload option available
            if analysis['has_upload'] and 'fileUpload' in selectors:
                logger.info("✓ Uploading document...")
                await browser.upload_document(document_path, selectors['fileUpload'])
            
            # Click submit
            if 'submitButton' in selectors:
                logger.info("✓ Submitting form...")
                try:
                    await browser.page.click(selectors['submitButton'])
                except:
                    pass
            
            # Wait for approval
            logger.info("⏳ Waiting for verification...")
            approved = await browser.wait_for_approval(
                approval_selector='.success, .approved, .verified, [class*="success"]',
                timeout=120000
            )
            
            if approved:
                # Try to extract discount code
                try:
                    code_selectors = [
                        '.code', '.discount-code', '.promo-code', 
                        '[class*="code"]', '[class*="discount"]'
                    ]
                    
                    for selector in code_selectors:
                        try:
                            code = await browser.extract_discount_code(selector)
                            if code and len(code) > 0:
                                return code
                        except:
                            continue
                    
                    # If no code found, take screenshot for manual extraction
                    await browser.screenshot('output/verification_success.png')
                    logger.info("✓ Verification approved (screenshot saved)")
                    return "APPROVED - Check output/verification_success.png"
                    
                except Exception as e:
                    logger.warning(f"Could not extract code: {e}")
                    return "APPROVED"
            else:
                # Take screenshot for debugging
                await browser.screenshot('output/verification_pending.png')
                logger.warning("⏸️  Verification pending (screenshot saved)")
                return None
                
        except Exception as e:
            logger.error(f"Submission error: {e}")
            return None
        finally:
            await browser.close()


async def main():
    """CLI interface for auto bypass"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🚀 Auto SheerID Bypass - Just provide the URL!',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Automatic bypass (easiest)
  python auto_bypass.py "https://verify.sheerid.com/..."
  
  # With university hint
  python auto_bypass.py "https://verify.sheerid.com/..." --hint "Stanford"
  
  # Show browser (for debugging)
  python auto_bypass.py "https://verify.sheerid.com/..." --show-browser
        """
    )
    
    parser.add_argument('url', help='SheerID verification URL')
    parser.add_argument('--hint', help='University hint (optional)')
    parser.add_argument('--show-browser', action='store_true',
                       help='Show browser window (default: headless)')
    
    args = parser.parse_args()
    
    # Run bypass
    bypass = AutoBypass(headless=not args.show_browser)
    results = await bypass.bypass(args.url, args.hint)
    
    # Print results
    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    print(f"Success: {'✅ YES' if results['success'] else '❌ NO'}")
    
    if results.get('strategy_used'):
        print(f"\n🎯 Winning Strategy: {results['strategy_used']}")
        print(f"🔢 Total Attempts: {results.get('total_attempts', 0)}")
    
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
        print(f"\n🎉 Discount Code: {results['code']}")
    
    if results['error']:
        print(f"\n❌ Error: {results['error']}")
    
    print("="*70)
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
