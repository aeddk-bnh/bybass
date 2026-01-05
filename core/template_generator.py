"""
Module: Dynamic Template Generator
Purpose: Automatically generate document templates for multiple universities
"""

import os
import random
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UniversityDatabase:
    """Database of universities with their information"""
    
    # Major universities worldwide
    UNIVERSITIES = {
        # US Universities
        'stanford': {
            'name': 'Stanford University',
            'domain': 'stanford.edu',
            'country': 'USA',
            'colors': ['#8C1515', '#FFFFFF'],
            'type': 'bill',
            'id_format': '{year}{num:04d}',
        },
        'harvard': {
            'name': 'Harvard University',
            'domain': 'harvard.edu',
            'country': 'USA',
            'colors': ['#A51C30', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{year}{num:05d}',
        },
        'mit': {
            'name': 'Massachusetts Institute of Technology',
            'domain': 'mit.edu',
            'country': 'USA',
            'colors': ['#A31F34', '#8A8B8C'],
            'type': 'bill',
            'id_format': '{num:09d}',
        },
        'berkeley': {
            'name': 'University of California, Berkeley',
            'domain': 'berkeley.edu',
            'country': 'USA',
            'colors': ['#003262', '#FDB515'],
            'type': 'enrollment',
            'id_format': '{year}{num:07d}',
        },
        'yale': {
            'name': 'Yale University',
            'domain': 'yale.edu',
            'country': 'USA',
            'colors': ['#00356B', '#FFFFFF'],
            'type': 'bill',
            'id_format': '{num:08d}',
        },
        'columbia': {
            'name': 'Columbia University',
            'domain': 'columbia.edu',
            'country': 'USA',
            'colors': ['#B9D9EB', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{year}_{num:05d}',
        },
        'princeton': {
            'name': 'Princeton University',
            'domain': 'princeton.edu',
            'country': 'USA',
            'colors': ['#FF8F00', '#000000'],
            'type': 'bill',
            'id_format': '{year}{num:06d}',
        },
        'cornell': {
            'name': 'Cornell University',
            'domain': 'cornell.edu',
            'country': 'USA',
            'colors': ['#B31B1B', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{num:09d}',
        },
        
        # UK Universities
        'oxford': {
            'name': 'University of Oxford',
            'domain': 'ox.ac.uk',
            'country': 'UK',
            'colors': ['#002147', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{num:07d}',
        },
        'cambridge': {
            'name': 'University of Cambridge',
            'domain': 'cam.ac.uk',
            'country': 'UK',
            'colors': ['#A3C1AD', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{year}{num:05d}',
        },
        'imperial': {
            'name': 'Imperial College London',
            'domain': 'imperial.ac.uk',
            'country': 'UK',
            'colors': ['#003E74', '#FFFFFF'],
            'type': 'bill',
            'id_format': '{year}{num:06d}',
        },
        
        # Vietnam Universities
        'hust': {
            'name': 'Hanoi University of Science and Technology',
            'domain': 'hust.edu.vn',
            'country': 'Vietnam',
            'colors': ['#ED1C24', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{year}{num:04d}',
        },
        'vnu': {
            'name': 'Vietnam National University, Hanoi',
            'domain': 'vnu.edu.vn',
            'country': 'Vietnam',
            'colors': ['#0033A0', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': 'VNU{year}{num:05d}',
        },
        'hcmus': {
            'name': 'Ho Chi Minh City University of Science',
            'domain': 'hcmus.edu.vn',
            'country': 'Vietnam',
            'colors': ['#003DA5', '#FFFFFF'],
            'type': 'bill',
            'id_format': '{year}{num:06d}',
        },
        
        # Canada
        'toronto': {
            'name': 'University of Toronto',
            'domain': 'utoronto.ca',
            'country': 'Canada',
            'colors': ['#00204E', '#FFFFFF'],
            'type': 'enrollment',
            'id_format': '{num:10d}',
        },
        'ubc': {
            'name': 'University of British Columbia',
            'domain': 'ubc.ca',
            'country': 'Canada',
            'colors': ['#002145', '#0055B7'],
            'type': 'bill',
            'id_format': '{year}{num:07d}',
        },
        
        # Australia
        'anu': {
            'name': 'Australian National University',
            'domain': 'anu.edu.au',
            'country': 'Australia',
            'colors': ['#FFD100', '#000000'],
            'type': 'enrollment',
            'id_format': 'u{num:07d}',
        },
        'sydney': {
            'name': 'University of Sydney',
            'domain': 'sydney.edu.au',
            'country': 'Australia',
            'colors': ['#E64626', '#FFFFFF'],
            'type': 'bill',
            'id_format': '{num:9d}',
        },
    }
    
    @classmethod
    def get_all_universities(cls) -> List[Dict]:
        """Get all universities as list"""
        return [
            {'key': key, **info}
            for key, info in cls.UNIVERSITIES.items()
        ]
    
    @classmethod
    def get_random_universities(cls, count: int = 5) -> List[Dict]:
        """Get random universities"""
        all_unis = cls.get_all_universities()
        count = min(count, len(all_unis))
        return random.sample(all_unis, count)
    
    @classmethod
    def get_university(cls, key: str) -> Dict:
        """Get specific university by key"""
        if key in cls.UNIVERSITIES:
            return {'key': key, **cls.UNIVERSITIES[key]}
        return None


class TemplateGenerator:
    """
    Dynamically generates document templates for any university
    """
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.db = UniversityDatabase()
    
    def generate_tuition_bill_template(self, university: Dict) -> tuple:
        """Generate tuition bill HTML template"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{university['name']} - Tuition Bill</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="document">
        <header>
            <div class="logo">{university['name']}</div>
            <h1>STUDENT ACCOUNT STATEMENT</h1>
            <div class="term">Academic Year {{{{ academic_year }}}}</div>
        </header>
        
        <section class="student-info">
            <div class="info-row">
                <span class="label">Student Name:</span>
                <span class="value">{{{{ name }}}}</span>
            </div>
            <div class="info-row">
                <span class="label">Student ID:</span>
                <span class="value">{{{{ id }}}}</span>
            </div>
            <div class="info-row">
                <span class="label">Term:</span>
                <span class="value">{{{{ term }}}}</span>
            </div>
            <div class="info-row">
                <span class="label">Program:</span>
                <span class="value">{{{{ program }}}}</span>
            </div>
        </section>
        
        <section class="charges">
            <h2>Charges</h2>
            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Tuition</td>
                        <td>{{{{ tuition }}}}</td>
                    </tr>
                    <tr>
                        <td>Student Services Fee</td>
                        <td>{{{{ services_fee }}}}</td>
                    </tr>
                    <tr>
                        <td>Health Insurance</td>
                        <td>{{{{ health_insurance }}}}</td>
                    </tr>
                    <tr class="total">
                        <td><strong>Total Due</strong></td>
                        <td><strong>{{{{ total_due }}}}</strong></td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <footer>
            <p>Statement Date: {{{{ statement_date }}}}</p>
            <p>{university['name']} - Office of the Bursar</p>
            <p class="confidential">CONFIDENTIAL - For Student Use Only</p>
        </footer>
    </div>
</body>
</html>"""
        
        css_content = f"""* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    background: white;
    padding: 40px;
}}

.document {{
    max-width: 850px;
    margin: 0 auto;
    background: white;
    border: 2px solid {university['colors'][0]};
}}

header {{
    background: {university['colors'][0]};
    color: {university['colors'][1]};
    padding: 30px;
    text-align: center;
}}

.logo {{
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 15px;
}}

h1 {{
    font-size: 28px;
    margin: 10px 0;
}}

.term {{
    font-size: 16px;
    margin-top: 10px;
}}

.student-info {{
    padding: 30px;
    background: #f9f9f9;
}}

.info-row {{
    display: flex;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
}}

.label {{
    font-weight: bold;
    width: 200px;
}}

.value {{
    flex: 1;
}}

.charges {{
    padding: 30px;
}}

.charges h2 {{
    color: {university['colors'][0]};
    margin-bottom: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}}

th {{
    background: {university['colors'][0]};
    color: {university['colors'][1]};
}}

.total td {{
    font-size: 18px;
    padding-top: 15px;
    border-top: 2px solid {university['colors'][0]};
}}

footer {{
    padding: 20px 30px;
    background: #f0f0f0;
    text-align: center;
    font-size: 12px;
}}

.confidential {{
    margin-top: 10px;
    color: #666;
    font-style: italic;
}}"""
        
        return html_content, css_content
    
    def generate_enrollment_template(self, university: Dict) -> tuple:
        """Generate enrollment verification template"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{university['name']} - Enrollment Verification</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="document">
        <header>
            <div class="logo">{university['name']}</div>
            <h1>ENROLLMENT VERIFICATION</h1>
        </header>
        
        <section class="verification-body">
            <p class="date">Date: {{{{ issue_date }}}}</p>
            
            <p class="statement">
                This is to certify that <strong>{{{{ name }}}}</strong>, 
                Student ID <strong>{{{{ id }}}}</strong>, is currently enrolled as a 
                <strong>{{{{ enrollment_status }}}}</strong> student at {university['name']} 
                for the <strong>{{{{ term }}}}</strong> term.
            </p>
            
            <div class="details">
                <div class="detail-row">
                    <span class="label">Program:</span>
                    <span class="value">{{{{ program }}}}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Academic Level:</span>
                    <span class="value">{{{{ level }}}}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Expected Graduation:</span>
                    <span class="value">{{{{ graduation_date }}}}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Enrollment Status:</span>
                    <span class="value">{{{{ enrollment_status }}}}</span>
                </div>
            </div>
            
            <div class="signature">
                <div class="signature-line"></div>
                <p><strong>{{{{ registrar_name }}}}</strong></p>
                <p>University Registrar</p>
                <p>{university['name']}</p>
            </div>
        </section>
        
        <footer>
            <p class="verification-code">Verification Code: {{{{ verification_code }}}}</p>
            <p class="contact">{university['name']} - Office of the Registrar</p>
            <p class="confidential">This is an official document</p>
        </footer>
    </div>
</body>
</html>"""
        
        css_content = f"""* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Arial', 'Helvetica', sans-serif;
    background: white;
    padding: 40px;
}}

.document {{
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border: 3px solid {university['colors'][0]};
}}

header {{
    background: {university['colors'][0]};
    color: {university['colors'][1]};
    padding: 40px;
    text-align: center;
}}

.logo {{
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 15px;
    text-transform: uppercase;
}}

h1 {{
    font-size: 30px;
    letter-spacing: 2px;
}}

.verification-body {{
    padding: 40px;
}}

.date {{
    text-align: right;
    margin-bottom: 30px;
    font-size: 14px;
}}

.statement {{
    line-height: 1.8;
    margin-bottom: 30px;
    font-size: 16px;
}}

.details {{
    background: #f5f5f5;
    padding: 25px;
    margin: 30px 0;
    border-left: 4px solid {university['colors'][0]};
}}

.detail-row {{
    display: flex;
    padding: 10px 0;
}}

.label {{
    font-weight: bold;
    width: 200px;
    color: {university['colors'][0]};
}}

.value {{
    flex: 1;
}}

.signature {{
    margin-top: 60px;
    text-align: center;
}}

.signature-line {{
    width: 300px;
    height: 2px;
    background: {university['colors'][0]};
    margin: 0 auto 10px;
}}

.signature p {{
    margin: 5px 0;
}}

footer {{
    padding: 20px;
    background: #f9f9f9;
    text-align: center;
    font-size: 12px;
    border-top: 2px solid {university['colors'][0]};
}}

.verification-code {{
    font-family: 'Courier New', monospace;
    font-weight: bold;
    margin-bottom: 10px;
}}

.confidential {{
    margin-top: 10px;
    color: #666;
    font-style: italic;
}}"""
        
        return html_content, css_content
    
    def create_template(self, university_key: str) -> bool:
        """Create template files for a university"""
        try:
            university = self.db.get_university(university_key)
            if not university:
                logger.error(f"University '{university_key}' not found")
                return False
            
            # Create directory
            template_dir = self.templates_dir / university_key
            template_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate template based on type
            if university['type'] == 'bill':
                html, css = self.generate_tuition_bill_template(university)
                filename = 'bill.html'
            else:
                html, css = self.generate_enrollment_template(university)
                filename = 'enrollment.html'
            
            # Write files
            (template_dir / filename).write_text(html, encoding='utf-8')
            (template_dir / 'style.css').write_text(css, encoding='utf-8')
            
            logger.info(f"✓ Created template for {university['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template for {university_key}: {e}")
            return False
    
    def create_all_templates(self) -> int:
        """Create templates for all universities"""
        logger.info("Generating templates for all universities...")
        count = 0
        
        for university_key in self.db.UNIVERSITIES.keys():
            if self.create_template(university_key):
                count += 1
        
        logger.info(f"✓ Generated {count} templates")
        return count
    
    def get_available_templates(self) -> List[Dict]:
        """Get list of all available templates"""
        templates = []
        
        for key, info in self.db.UNIVERSITIES.items():
            template_dir = self.templates_dir / key
            if template_dir.exists():
                filename = 'bill.html' if info['type'] == 'bill' else 'enrollment.html'
                templates.append({
                    'key': key,
                    'name': info['name'],
                    'domain': info['domain'],
                    'template': f"{key}/{filename}",
                    'country': info['country'],
                    'id_format': info['id_format']
                })
        
        return templates
