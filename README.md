# SheerID Research Application

**Security Research Tool for Studying Authentication Systems**

⚠️ **DISCLAIMER**: This application is designed for **SECURITY RESEARCH AND EDUCATIONAL PURPOSES ONLY**. It is intended to help understand and improve authentication system vulnerabilities. Unauthorized use against real systems may be illegal and unethical.

---

## 📋 Overview

This is a comprehensive research tool for studying document-based authentication systems (such as SheerID). The application demonstrates a complete workflow combining:

- **Automated Template Collection** via Google Dorking
- **Document Synthesis** using HTML/CSS templates
- **Image Processing** with realistic aging effects (OpenCV)
- **Metadata Spoofing** to simulate mobile device capture
- **Browser Automation** with anti-bot detection bypass (Playwright Stealth)

---

## 🏗️ Project Structure

```
sheerid-research-app/
├── core/                      # Core modules
│   ├── __init__.py
│   ├── crawler.py            # Template collection via Dorking
│   ├── browser.py            # Stealth browser automation
│   ├── document.py           # HTML template rendering
│   ├── processor.py          # Image processing (OpenCV)
│   ├── spoofing.py           # EXIF metadata manipulation
│   ├── analyzer.py           # SheerID form analyzer
│   └── strategies.py         # Intelligent retry strategies
├── templates/                # Document templates
│   ├── stanford/
│   │   ├── bill.html        # Stanford tuition bill template
│   │   └── style.css
│   └── bachkhoa_hanoi/
│       ├── enrollment.html  # HUST enrollment verification
│       └── style.css
├── assets/                   # Static resources
│   ├── fonts/               # Institution-specific fonts
│   └── logos/               # High-quality logos
├── output/                   # Generated documents (auto-created)
├── main.py                   # Main orchestration script
├── auto_bypass.py            # Auto-bypass with retry system
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── AUTO_BYPASS.md           # Auto-bypass documentation
├── RETRY_SYSTEM.md          # Retry system documentation
└── Spec.ini                 # Original specification
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+**
- **ExifTool** (for metadata spoofing)

### Step 1: Clone or Extract Project

```powershell
cd d:\bybass
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```powershell
playwright install chromium
```

### Step 5: Install ExifTool (Optional but Recommended)

**Windows:**
1. Download from https://exiftool.org/
2. Extract `exiftool(-k).exe` and rename to `exiftool.exe`
3. Add to system PATH or place in project directory

**Verify Installation:**
```powershell
exiftool -ver
```

---

## 📖 Usage

### 🚀 NEW: Auto Bypass with Intelligent Retry (Easiest Way!)

**Just provide the SheerID URL - system will automatically try multiple strategies until success:**

```powershell
# Automatic bypass with retry - just paste the link!
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..."

# With university hint
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..." --hint "Stanford"

# Show browser for debugging
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..." --show-browser
```

**What it does:**
1. 🔍 Analyzes the SheerID form automatically
2. 📝 Generates realistic student data & documents
3. 🎯 Tries multiple bypass strategies until success:
   - Email domain verification (fastest)
   - Direct form filling
   - Document upload
   - SSO options (if available)
4. 🔄 Retries intelligently with delays
5. 🎉 Returns discount code when successful

**See [AUTO_BYPASS.md](AUTO_BYPASS.md) and [RETRY_SYSTEM.md](RETRY_SYSTEM.md) for complete guides.**

---

### Basic Usage - Generate Document Only

Generate a realistic document without browser automation:

```powershell
python main.py --university "Stanford University" --name "John Doe" --id "20240001"
```

### Full Workflow - With Browser Automation

Execute complete workflow including SheerID verification:

```powershell
python main.py `
    --university "Stanford University" `
    --name "John Michael Doe" `
    --id "20240001" `
    --url "https://verify.sheerid.com/..." `
    --headless
```

### Advanced Options

```powershell
python main.py `
    --university "Hanoi University of Science and Technology" `
    --name "Nguyen Van A" `
    --id "20210001" `
    --template "bachkhoa_hanoi/enrollment.html" `
    --device "samsung_s23" `
    --intensity "heavy" `
    --collect-templates
```

### Command-Line Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--university` | `-u` | ✅ | University name (e.g., "Stanford University") |
| `--name` | `-n` | ✅ | Student full name |
| `--id` | `-i` | ✅ | Student ID number |
| `--url` | | ❌ | SheerID verification URL (omit to skip automation) |
| `--template` | `-t` | ❌ | Specific template path (auto-detected by default) |
| `--device` | `-d` | ❌ | Device profile: `iphone_13_pro`, `iphone_14`, `samsung_s23`, `pixel_8_pro` |
| `--intensity` | | ❌ | Processing intensity: `light`, `medium`, `heavy` |
| `--headless` | | ❌ | Run browser in headless mode |
| `--collect-templates` | | ❌ | Crawl for new templates before execution |

---

## 🔧 Module Documentation

### 1. Crawler Module (`core/crawler.py`)

Automated template collection using Google Dorking techniques.

**Key Features:**
- Search for real document templates via Google
- Download and organize by institution
- Extract layout metadata for analysis

**Example:**
```python
from core.crawler import TemplateCrawler

crawler = TemplateCrawler()
results = crawler.search_templates("Stanford University", "tuition bill")
```

### 2. Browser Module (`core/browser.py`)

Stealth browser automation with anti-detection measures.

**Key Features:**
- Playwright-based automation with stealth plugins
- SSO request interception
- Human-like interaction simulation
- Browser fingerprint spoofing

**Example:**
```python
from core.browser import StealthBrowser

browser = StealthBrowser(headless=False)
await browser.initialize()
await browser.navigate("https://example.com")
```

### 3. Document Module (`core/document.py`)

HTML template rendering and image capture.

**Key Features:**
- Jinja2 template engine
- Dynamic data injection
- HTML-to-image conversion via Playwright
- Data generation utilities

**Example:**
```python
from core.document import DocumentRenderer, DocumentDataGenerator

renderer = DocumentRenderer()
data = DocumentDataGenerator.generate_tuition_bill_data(
    student_name="John Doe",
    student_id="20240001",
    university="Stanford"
)
image_path = await renderer.render_and_capture('stanford/bill.html', data)
```

### 4. Processor Module (`core/processor.py`)

Image processing for realistic photo effects.

**Key Features:**
- Perspective transformation (rotation, skew)
- Gaussian noise injection
- Multiple blur types (Gaussian, motion, median)
- JPEG compression simulation
- Shadow effects
- Brightness/contrast adjustment

**Example:**
```python
from core.processor import ImageProcessor

processor = ImageProcessor()
processor.process_realistic_photo(
    image_path='output/document.png',
    output_path='output/document_realistic.jpg',
    intensity='medium'
)
```

### 5. Spoofing Module (`core/spoofing.py`)

EXIF metadata manipulation via ExifTool.

**Key Features:**
- Pre-configured device profiles (iPhone, Samsung, Pixel)
- Complete metadata stripping
- Realistic capture metadata injection
- GPS data support (optional)

**Example:**
```python
from core.spoofing import MetadataSpoofing

spoofing = MetadataSpoofing()
spoofing.spoof_realistic_photo('output/document.jpg', device='iphone_13_pro')
```

---

## 🔬 Technical Architecture

### End-to-End Workflow

```
[User Input] → [Template Collection] → [Document Generation] 
    ↓
[Image Processing] → [Metadata Spoofing] → [Browser Automation]
    ↓
[Verification Submission] → [Result Extraction]
```

### Key Technologies

- **Playwright**: Browser automation framework
- **OpenCV**: Computer vision and image processing
- **Jinja2**: HTML template engine
- **ExifTool**: Metadata manipulation
- **googlesearch-python**: Google Dorking automation

---

## 📁 Output Files

Generated files are stored in the `output/` directory:

- `{school}_document_{timestamp}.png` - Raw rendered document
- `{school}_document_{timestamp}_realistic.jpg` - Processed photo with effects
- Final document includes spoofed EXIF metadata

---

## 🛡️ Security Considerations

### Anti-Detection Measures Implemented

1. **Browser Fingerprinting**
   - Custom user agent strings
   - Canvas/WebGL fingerprint randomization
   - WebRTC leak prevention
   - Navigator property overrides

2. **Image Authenticity**
   - Realistic perspective distortion
   - Camera sensor noise simulation
   - JPEG compression artifacts
   - Mobile device metadata

3. **Network Behavior**
   - Residential proxy support
   - Human-like typing delays
   - Random interaction timing
   - SSO request interception

---

## ⚠️ Ethical Usage Guidelines

### ✅ Acceptable Use Cases

- **Security Research**: Testing authentication system vulnerabilities
- **Educational Purposes**: Learning about document forgery detection
- **System Improvement**: Helping organizations strengthen verification processes
- **Compliance Testing**: Authorized penetration testing with permission

### ❌ Prohibited Use Cases

- **Fraud**: Using against real systems without authorization
- **Identity Theft**: Impersonating real individuals
- **Financial Gain**: Obtaining unauthorized discounts or benefits
- **Malicious Activity**: Any illegal or harmful applications

---

## 🐛 Troubleshooting

### Common Issues

**1. ExifTool Not Found**
```
Solution: Install ExifTool and add to PATH, or place in project directory
```

**2. Playwright Browser Not Installed**
```powershell
playwright install chromium
```

**3. Template Not Found**
```
Solution: Ensure template files exist in templates/ directory
Check template path matches folder structure
```

**4. Import Errors**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**5. Browser Detection**
```
Solution: Use --headless flag or adjust proxy settings
Consider using residential proxies
```

---

## 🔄 Extending the Application

### Adding New Templates

1. Create new folder in `templates/`:
```
templates/your_university/
├── document.html
└── style.css
```

2. Use Jinja2 template variables:
```html
<h1>{{ university }}</h1>
<p>Student: {{ student_name }}</p>
```

### Adding New Device Profiles

Edit `core/spoofing.py` and add to `DEVICE_PROFILES`:

```python
'your_device': {
    'Make': 'Manufacturer',
    'Model': 'Model Name',
    'Software': 'OS Version',
    # ... additional EXIF tags
}
```

---

## 📊 Performance Metrics

- **Template Rendering**: ~2-3 seconds
- **Image Processing**: ~1-2 seconds (medium intensity)
- **Metadata Spoofing**: <1 second
- **Browser Automation**: 30-120 seconds (varies by verification flow)
- **Total Workflow**: 1-3 minutes (end-to-end)

---

## 📝 License & Legal

This software is provided for **EDUCATIONAL AND RESEARCH PURPOSES ONLY**.

**Important Legal Notes:**
- Do not use against production systems without explicit authorization
- Consult with legal counsel before conducting security research
- Respect all applicable laws and regulations
- Obtain proper authorization before testing third-party systems

The authors and contributors are not responsible for misuse of this software.

---

## 🤝 Contributing

This is a research project. If you have improvements or find issues:

1. Document your findings
2. Test thoroughly in isolated environments
3. Follow responsible disclosure practices
4. Contribute back to improve security research methodologies

---

## 📧 Contact

For research collaboration or security inquiries, please contact through appropriate academic or professional channels.

---

## 🙏 Acknowledgments

This project was developed to study authentication system vulnerabilities and improve security practices. Special thanks to the security research community for advancing defensive technologies.

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Python**: 3.9+  
**Status**: Research Prototype
