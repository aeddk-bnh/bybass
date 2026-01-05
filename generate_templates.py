"""
Generate all university templates
"""

import sys
import logging
from core.template_generator import TemplateGenerator, UniversityDatabase

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    print("="*70)
    print("🎓 UNIVERSITY TEMPLATE GENERATOR")
    print("="*70)
    print()
    
    gen = TemplateGenerator()
    db = UniversityDatabase()
    
    # Show available universities
    print(f"📚 Available Universities: {len(db.UNIVERSITIES)}")
    print()
    
    for key, info in db.UNIVERSITIES.items():
        country_flag = {
            'USA': '🇺🇸',
            'UK': '🇬🇧',
            'Vietnam': '🇻🇳',
            'Canada': '🇨🇦',
            'Australia': '🇦🇺'
        }.get(info['country'], '🌍')
        
        print(f"{country_flag} {info['name']}")
        print(f"   Domain: {info['domain']}")
        print(f"   Template: {info['type']}")
        print()
    
    # Generate all
    print("="*70)
    print("Generating templates...")
    print("="*70)
    print()
    
    count = gen.create_all_templates()
    
    print()
    print("="*70)
    print(f"✅ SUCCESS!")
    print(f"Generated {count} templates in templates/ directory")
    print("="*70)
    print()
    
    # Show available templates
    templates = gen.get_available_templates()
    print(f"📋 Available templates: {len(templates)}")
    for t in templates[:10]:  # Show first 10
        print(f"  • {t['name']} ({t['country']})")
    
    if len(templates) > 10:
        print(f"  ... and {len(templates) - 10} more")
    
    print()
    print("💡 Usage:")
    print("  python auto_bypass.py 'URL' --multi-university")
    print("  → System will automatically try different universities until success!")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
