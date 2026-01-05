"""
Production Workflow Runner
Simplified interface for running main.py with common configurations
"""

import os
import sys
import subprocess
from datetime import datetime

# Configuration
PYTHON_EXE = "D:/bybass/.venv/Scripts/python.exe"
MAIN_SCRIPT = "main.py"

# Production scenarios
SCENARIOS = {
    "stanford_student": {
        "university": "Stanford University",
        "template": "stanford/bill.html",
        "device": "iphone_13_pro",
        "intensity": "medium"
    },
    "hust_student": {
        "university": "Hanoi University of Science and Technology",
        "template": "bachkhoa_hanoi/enrollment.html",
        "device": "samsung_s23",
        "intensity": "medium"
    }
}


def run_workflow(scenario_name, student_name, student_id, sheerid_url=None, headless=True):
    """
    Run production workflow with predefined scenario
    
    Args:
        scenario_name: Name of scenario from SCENARIOS dict
        student_name: Student full name
        student_id: Student ID number
        sheerid_url: Optional SheerID URL for full automation
        headless: Run browser in headless mode
    """
    if scenario_name not in SCENARIOS:
        print(f"❌ Unknown scenario: {scenario_name}")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        return 1
    
    scenario = SCENARIOS[scenario_name]
    
    # Build command
    cmd = [
        PYTHON_EXE,
        MAIN_SCRIPT,
        "--university", scenario["university"],
        "--name", student_name,
        "--id", student_id,
        "--template", scenario["template"],
        "--device", scenario["device"],
        "--intensity", scenario["intensity"]
    ]
    
    if sheerid_url:
        cmd.extend(["--url", sheerid_url])
    
    if headless:
        cmd.append("--headless")
    
    # Log command
    print("="*60)
    print(f"Running production workflow: {scenario_name}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print(f"Student: {student_name} ({student_id})")
    print(f"University: {scenario['university']}")
    print(f"Device: {scenario['device']}")
    print(f"Intensity: {scenario['intensity']}")
    print("="*60)
    
    # Execute
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def batch_run(scenario_name, students_csv):
    """
    Run workflow for multiple students from CSV file
    
    CSV format: name,id
    Example:
        John Doe,20240001
        Jane Smith,20240002
    """
    import csv
    
    if not os.path.exists(students_csv):
        print(f"❌ CSV file not found: {students_csv}")
        return 1
    
    print(f"📋 Batch processing from: {students_csv}")
    
    with open(students_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            print(f"\n{'='*60}")
            print(f"Processing #{i}: {row['name']}")
            print(f"{'='*60}")
            
            run_workflow(
                scenario_name=scenario_name,
                student_name=row['name'],
                student_id=row['id']
            )
    
    print(f"\n✅ Batch processing complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Production Workflow Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single run - Stanford student
  python run_production.py stanford_student "John Doe" "20240001"
  
  # With SheerID URL and visible browser
  python run_production.py stanford_student "John Doe" "20240001" \\
      --url "https://verify.sheerid.com/..." --no-headless
  
  # Batch processing from CSV
  python run_production.py stanford_student --batch students.csv
        """
    )
    
    parser.add_argument('scenario', choices=list(SCENARIOS.keys()),
                       help='Scenario to run')
    parser.add_argument('name', nargs='?',
                       help='Student name')
    parser.add_argument('id', nargs='?',
                       help='Student ID')
    parser.add_argument('--url',
                       help='SheerID verification URL')
    parser.add_argument('--no-headless', action='store_true',
                       help='Show browser window')
    parser.add_argument('--batch',
                       help='CSV file with multiple students')
    
    args = parser.parse_args()
    
    if args.batch:
        sys.exit(batch_run(args.scenario, args.batch))
    else:
        if not args.name or not args.id:
            parser.error("name and id are required unless using --batch")
        
        sys.exit(run_workflow(
            scenario_name=args.scenario,
            student_name=args.name,
            student_id=args.id,
            sheerid_url=args.url,
            headless=not args.no_headless
        ))
