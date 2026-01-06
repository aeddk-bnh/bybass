"""
Module: Bypass Strategy Manager
Purpose: Intelligent retry system with multiple bypass strategies
"""

import asyncio
import random
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StrategyResult:
    """Result of a bypass strategy attempt"""
    success: bool
    strategy_name: str
    code: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 1
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class BypassStrategy:
    """Base class for bypass strategies"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Execute the strategy - must be implemented by subclasses"""
        raise NotImplementedError


class FormFillStrategy(BypassStrategy):
    """Strategy: Fill form with generated data"""
    
    def __init__(self):
        super().__init__(
            name="Form Fill",
            description="Fill all required fields with realistic generated data"
        )
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Fill form directly"""
        logger.info(f"[{self.name}] Attempting direct form fill...")
        
        try:
            browser = context['browser']
            analysis = context['analysis']
            student_data = context['student_data']
            
            # Fill all detected fields
            fields = analysis.get('form_selectors', {})
            
            for field_name, selector in fields.items():
                try:
                    value = self._get_value_for_field(field_name, student_data)
                    if value:
                        await browser.page.fill(selector, value)
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                except Exception as e:
                    logger.warning(f"Failed to fill {field_name}: {e}")
            
            # Try to submit
            submit_button = await browser.page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Verify"), button:has-text("Submit")')
            if submit_button:
                await submit_button.click()
                await asyncio.sleep(3)
                
                # Check for success indicators
                success = await self._check_success(browser.page)
                if success:
                    code = await self._extract_code(browser.page)
                    return StrategyResult(True, self.name, code=code)
            
            return StrategyResult(False, self.name, error="Submit failed or not found")
            
        except Exception as e:
            return StrategyResult(False, self.name, error=str(e))
    
    def _get_value_for_field(self, field_name: str, data: Dict) -> Optional[str]:
        """Map field names to student data"""
        field_map = {
            'firstName': data.get('first_name'),
            'lastName': data.get('last_name'),
            'email': data.get('email'),
            'studentId': data.get('student_id'),
            'birthDate': data.get('birth_date'),
            'phone': data.get('phone'),
        }
        return field_map.get(field_name)
    
    async def _check_success(self, page) -> bool:
        """Check if verification succeeded"""
        success_indicators = [
            'success', 'verified', 'approved', 'congratulations',
            'discount', 'code', 'offer'
        ]
        page_text = await page.content()
        return any(indicator in page_text.lower() for indicator in success_indicators)
    
    async def _extract_code(self, page) -> Optional[str]:
        """Try to extract discount code"""
        try:
            # Look for code patterns
            text = await page.inner_text('body')
            import re
            
            # Common code patterns
            patterns = [
                r'code[:\s]+([A-Z0-9]{6,})',
                r'discount[:\s]+([A-Z0-9]{6,})',
                r'\b([A-Z0-9]{8,12})\b'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        return None


class DocumentUploadStrategy(BypassStrategy):
    """Strategy: Upload document proof"""
    
    def __init__(self):
        super().__init__(
            name="Document Upload",
            description="Upload generated document as verification proof"
        )
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Upload document"""
        logger.info(f"[{self.name}] Attempting document upload...")
        
        try:
            browser = context['browser']
            document_path = context.get('document_path')
            student_data = context['student_data']
            
            if not document_path:
                return StrategyResult(False, self.name, error="No document available")
            
            # Fill basic fields first
            await browser.fill_form({
                'firstName': student_data.get('first_name'),
                'lastName': student_data.get('last_name'),
                'email': student_data.get('email'),
            })
            
            # Upload document
            uploaded = await browser.upload_document(document_path)
            if not uploaded:
                return StrategyResult(False, self.name, error="Upload failed")
            
            await asyncio.sleep(2)
            
            # Wait for approval
            approved, code = await browser.wait_for_approval(timeout=10)
            
            if approved:
                return StrategyResult(True, self.name, code=code)
            
            return StrategyResult(False, self.name, error="Not approved yet")
            
        except Exception as e:
            return StrategyResult(False, self.name, error=str(e))


class SSOStrategy(BypassStrategy):
    """Strategy: Try SSO login option"""
    
    def __init__(self):
        super().__init__(
            name="SSO Login",
            description="Attempt SSO authentication if available"
        )
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Try SSO"""
        logger.info(f"[{self.name}] Checking SSO option...")
        
        analysis = context['analysis']
        if not analysis.get('has_sso'):
            return StrategyResult(False, self.name, error="No SSO available")
        
        # SSO typically requires real credentials - skip for now
        return StrategyResult(False, self.name, error="SSO requires real credentials")


class EmailDomainStrategy(BypassStrategy):
    """Strategy: Use university email domain"""
    
    def __init__(self):
        super().__init__(
            name="Email Domain",
            description="Generate and use university email address"
        )
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Try with university email"""
        logger.info(f"[{self.name}] Attempting with university email domain...")
        
        try:
            browser = context['browser']
            student_data = context['student_data']
            university = context['analysis'].get('university', 'stanford.edu')
            
            # Generate university email
            email = f"{student_data['first_name'].lower()}.{student_data['last_name'].lower()}@{university}"
            
            # Fill form with university email
            form_data = {
                'firstName': student_data['first_name'],
                'lastName': student_data['last_name'],
                'email': email,
                'studentId': student_data['student_id'],
            }
            
            await browser.fill_form(form_data)
            await asyncio.sleep(2)
            
            # Check for instant verification
            page_text = await browser.page.content()
            if 'verified' in page_text.lower() or 'success' in page_text.lower():
                code = await self._extract_code(browser.page)
                return StrategyResult(True, self.name, code=code)
            
            return StrategyResult(False, self.name, error="Email not instantly verified")
            
        except Exception as e:
            return StrategyResult(False, self.name, error=str(e))
    
    async def _extract_code(self, page) -> Optional[str]:
        """Extract discount code"""
        try:
            text = await page.inner_text('body')
            import re
            patterns = [
                r'code[:\s]+([A-Z0-9]{6,})',
                r'\b([A-Z0-9]{8,12})\b'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        return None


class MultiUniversityStrategy(BypassStrategy):
    """Strategy: Try different universities automatically"""
    
    def __init__(self, country_filter: str = 'USA'):
        super().__init__(
            name="Multi-University Rotation",
            description=f"Automatically try documents from different {country_filter} universities"
        )
        self.tried_universities = set()
        self.country_filter = country_filter
    
    async def execute(self, context: Dict) -> StrategyResult:
        """Try with different university template"""
        from core.template_generator import TemplateGenerator, UniversityDatabase
        from core.document import DocumentRenderer, DocumentDataGenerator
        from core.processor import ImageProcessor
        from core.spoofing import MetadataSpoofing
        import random
        
        logger.info(f"[{self.name}] Trying different {self.country_filter} university...")
        
        try:
            # Get available universities not yet tried (filtered by country)
            all_universities = UniversityDatabase.get_all_universities()
            available = [
                u for u in all_universities 
                if u['key'] not in self.tried_universities 
                and u['country'] == self.country_filter
            ]
            
            if not available:
                return StrategyResult(False, self.name, error=f"All {self.country_filter} universities tried")
            
            # Pick random university
            university = random.choice(available)
            self.tried_universities.add(university['key'])
            
            logger.info(f"  → Trying: {university['name']}")
            
            # Generate template if not exists
            gen = TemplateGenerator()
            gen.create_template(university['key'])
            
            # Generate new student data for this university
            renderer = DocumentRenderer()
            data_gen = DocumentDataGenerator()
            processor = ImageProcessor()
            spoofing = MetadataSpoofing()
            
            # Create student identity
            first_name = random.choice(['John', 'Michael', 'David', 'James', 'Sarah', 'Emily'])
            last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])
            student_name = f"{first_name} {last_name}"
            
            # Generate student ID
            year = random.randint(2020, 2024)
            num = random.randint(1, 9999)
            student_id = university['id_format'].format(year=year, num=num)
            
            # Generate document
            template_file = 'bill.html' if university['type'] == 'bill' else 'enrollment.html'
            template_path = f"{university['key']}/{template_file}"
            
            if university['type'] == 'bill':
                doc_data = data_gen.generate_tuition_bill_data(student_name, student_id, university['name'])
            else:
                doc_data = data_gen.generate_enrollment_verification_data(student_name, student_id, university['name'])
            
            # Render and process
            image_path = await renderer.render_and_capture(template_path, doc_data)
            processed_path = processor.process_realistic_photo(
                image_path,
                image_path.replace('.png', '_realistic.jpg'),
                'medium'
            )
            spoofing.spoof_realistic_photo(processed_path, 'iphone_14')
            
            # Try upload
            browser = context['browser']
            email = f"{first_name.lower()}.{last_name.lower()}@{university['domain']}"
            
            form_data = {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'studentId': student_id,
            }
            
            await browser.fill_form(form_data)
            await asyncio.sleep(1)
            
            # Try upload if available
            uploaded = await browser.upload_document(processed_path)
            if uploaded:
                await asyncio.sleep(2)
                
                # Check success
                page_text = await browser.page.content()
                if 'success' in page_text.lower() or 'verified' in page_text.lower():
                    code = await self._extract_code(browser.page)
                    return StrategyResult(True, f"{self.name} ({university['name']})", code=code)
            
            return StrategyResult(False, self.name, error=f"{university['name']} didn't work")
            
        except Exception as e:
            logger.error(f"Error in multi-university: {e}")
            return StrategyResult(False, self.name, error=str(e))
    
    async def _extract_code(self, page) -> Optional[str]:
        """Extract code"""
        try:
            text = await page.inner_text('body')
            import re
            patterns = [r'code[:\s]+([A-Z0-9]{6,})', r'\b([A-Z0-9]{8,12})\b']
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        return None


class StrategyManager:
    """
    Manages multiple bypass strategies and intelligent retry logic
    """
    
    def __init__(self, enable_multi_university: bool = True, country_filter: str = 'USA'):
        self.strategies: List[BypassStrategy] = []
        self.max_attempts_per_strategy = 3
        self.max_total_attempts = 15  # Increased for multi-university
        self.enable_multi_university = enable_multi_university
        self.country_filter = country_filter
        
        # Register all strategies
        self._register_strategies()
    
    def _register_strategies(self):
        """Register available strategies in priority order"""
        self.strategies = [
            EmailDomainStrategy(),      # Fast, often works instantly
            FormFillStrategy(),          # Basic form filling
            DocumentUploadStrategy(),    # More complex but thorough
        ]
        
        # Add multi-university rotation
        if self.enable_multi_university:
            self.strategies.append(MultiUniversityStrategy(country_filter=self.country_filter))
        
        # SSO as fallback
        self.strategies.append(SSOStrategy())
        
        logger.info(f"Registered {len(self.strategies)} bypass strategies")
        if self.enable_multi_university:
            logger.info(f"Multi-University mode: {self.country_filter} universities only")
    
    async def execute_with_retry(
        self, 
        context: Dict,
        on_attempt: Optional[Callable] = None
    ) -> StrategyResult:
        """
        Execute strategies with intelligent retry until success
        
        Args:
            context: Context with browser, analysis, student_data, etc.
            on_attempt: Optional callback for each attempt
            
        Returns:
            Final strategy result
        """
        logger.info("\n" + "="*70)
        logger.info("🎯 STARTING INTELLIGENT RETRY SYSTEM")
        logger.info(f"📋 {len(self.strategies)} strategies available")
        logger.info("="*70 + "\n")
        
        total_attempts = 0
        all_results = []
        
        for strategy_round in range(self.max_attempts_per_strategy):
            logger.info(f"\n🔄 ROUND {strategy_round + 1}/{self.max_attempts_per_strategy}")
            logger.info("-" * 70)
            
            for strategy in self.strategies:
                if total_attempts >= self.max_total_attempts:
                    logger.warning("⚠️  Max total attempts reached")
                    break
                
                total_attempts += 1
                
                logger.info(f"\n[Attempt {total_attempts}] Strategy: {strategy.name}")
                logger.info(f"Description: {strategy.description}")
                
                # Callback for progress updates
                if on_attempt:
                    on_attempt(strategy.name, total_attempts)
                
                # Execute strategy
                result = await strategy.execute(context)
                result.attempts = total_attempts
                all_results.append(result)
                
                # Log result
                if result.success:
                    logger.info(f"✅ SUCCESS with {strategy.name}!")
                    if result.code:
                        logger.info(f"🎉 Code: {result.code}")
                    return result
                else:
                    logger.info(f"❌ Failed: {result.error}")
                
                # Small delay between strategies
                await asyncio.sleep(random.uniform(1.5, 3.0))
            
            # Delay between rounds
            if strategy_round < self.max_attempts_per_strategy - 1:
                delay = random.uniform(3, 5)
                logger.info(f"\n⏳ Waiting {delay:.1f}s before next round...")
                await asyncio.sleep(delay)
        
        # All strategies failed
        logger.info("\n" + "="*70)
        logger.warning("⚠️  ALL STRATEGIES EXHAUSTED")
        logger.info(f"Total attempts: {total_attempts}")
        logger.info("="*70)
        
        # Return last result
        return all_results[-1] if all_results else StrategyResult(
            False, 
            "None", 
            error="No strategies executed"
        )
    
    def add_strategy(self, strategy: BypassStrategy, priority: int = -1):
        """Add custom strategy"""
        if priority >= 0:
            self.strategies.insert(priority, strategy)
        else:
            self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.name}")
