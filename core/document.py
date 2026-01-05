"""
Module: Document Renderer
Purpose: HTML template rendering and conversion to image/PDF
Technology: Jinja2 + Playwright for screenshot capture
"""

import os
import asyncio
from jinja2 import Environment, FileSystemLoader, Template
from playwright.async_api import async_playwright
from typing import Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentRenderer:
    """
    Renders HTML templates with dynamic data and captures as images
    """
    
    def __init__(self, templates_dir: str = "templates", output_dir: str = "output"):
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def render_template(self, template_name: str, data: Dict) -> str:
        """
        Render HTML template with provided data
        
        Args:
            template_name: Name of template file (e.g., 'stanford/bill.html')
            data: Dictionary with template variables
            
        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            html = template.render(**data)
            logger.info(f"Rendered template: {template_name}")
            return html
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise
    
    def render_from_string(self, html_template: str, data: Dict) -> str:
        """
        Render HTML from string template
        
        Args:
            html_template: HTML template string
            data: Dictionary with template variables
            
        Returns:
            Rendered HTML string
        """
        template = Template(html_template)
        return template.render(**data)
    
    async def html_to_image(self, html_content: str, output_path: str, 
                           width: int = 1200, height: int = 1600) -> str:
        """
        Convert HTML to image using Playwright screenshot
        
        Args:
            html_content: Rendered HTML content
            output_path: Path to save the image
            width: Viewport width
            height: Viewport height
            
        Returns:
            Path to generated image
        """
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        
        page = await browser.new_page(viewport={'width': width, 'height': height})
        
        # Set HTML content
        await page.set_content(html_content, wait_until='networkidle')
        
        # Wait for fonts and images to load
        await asyncio.sleep(2)
        
        # Take screenshot
        await page.screenshot(path=output_path, full_page=True)
        
        await browser.close()
        await playwright.stop()
        
        logger.info(f"Generated image: {output_path}")
        return output_path
    
    async def render_and_capture(self, template_name: str, data: Dict, 
                                output_filename: Optional[str] = None) -> str:
        """
        Complete workflow: render template and capture as image
        
        Args:
            template_name: Template file name
            data: Template data
            output_filename: Custom output filename (auto-generated if None)
            
        Returns:
            Path to generated image
        """
        # Render HTML
        html = self.render_template(template_name, data)
        
        # Generate output filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            school = template_name.split('/')[0]
            output_filename = f"{school}_document_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Convert to image
        await self.html_to_image(html, output_path)
        
        return output_path
    
    def save_html_preview(self, template_name: str, data: Dict, 
                         preview_filename: Optional[str] = None) -> str:
        """
        Save rendered HTML for preview/debugging
        
        Args:
            template_name: Template file name
            data: Template data
            preview_filename: Output HTML filename
            
        Returns:
            Path to saved HTML file
        """
        html = self.render_template(template_name, data)
        
        if not preview_filename:
            preview_filename = template_name.replace('/', '_').replace('.html', '_preview.html')
        
        preview_path = os.path.join(self.output_dir, preview_filename)
        
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Saved HTML preview: {preview_path}")
        return preview_path


class DocumentDataGenerator:
    """
    Generates realistic data for document templates
    """
    
    @staticmethod
    def generate_tuition_bill_data(student_name: str, student_id: str, 
                                   university: str, amount: float = 15000.00) -> Dict:
        """
        Generate data for tuition bill template
        
        Args:
            student_name: Full name of student
            student_id: Student ID number
            university: University name
            amount: Tuition amount
            
        Returns:
            Dictionary with all template variables
        """
        now = datetime.now()
        
        return {
            'university': university,
            'student_name': student_name,
            'student_id': student_id,
            'billing_date': now.strftime("%B %d, %Y"),
            'due_date': (now.replace(month=now.month+1 if now.month < 12 else 1)).strftime("%B %d, %Y"),
            'semester': f"{'Spring' if now.month <= 6 else 'Fall'} {now.year}",
            'tuition_amount': f"${amount:,.2f}",
            'fees_amount': f"${amount * 0.1:,.2f}",
            'total_amount': f"${amount * 1.1:,.2f}",
            'account_number': student_id,
            'payment_status': 'Pending'
        }
    
    @staticmethod
    def generate_enrollment_verification_data(student_name: str, student_id: str,
                                              university: str, program: str = "Computer Science") -> Dict:
        """
        Generate data for enrollment verification template
        """
        now = datetime.now()
        
        return {
            'university': university,
            'student_name': student_name,
            'student_id': student_id,
            'program': program,
            'enrollment_status': 'Full-time',
            'academic_year': f"{now.year}-{now.year+1}",
            'semester': f"{'Spring' if now.month <= 6 else 'Fall'} {now.year}",
            'issue_date': now.strftime("%B %d, %Y"),
            'registrar_name': 'Office of the Registrar',
            'verification_code': f"VER-{now.year}-{student_id}"
        }


async def main_example():
    """Example usage"""
    renderer = DocumentRenderer()
    generator = DocumentDataGenerator()
    
    # Generate data
    data = generator.generate_tuition_bill_data(
        student_name="John Michael Doe",
        student_id="20240001",
        university="Stanford University",
        amount=18500.00
    )
    
    # Render and capture
    image_path = await renderer.render_and_capture('stanford/bill.html', data)
    print(f"Document generated: {image_path}")


if __name__ == "__main__":
    asyncio.run(main_example())
