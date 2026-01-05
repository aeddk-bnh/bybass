# Production Workflows Guide

## 🚀 Quick Start for Production Use

### Method 1: Using Production Runner (Recommended)

The `run_production.py` script provides a simplified interface for common scenarios.

#### Single Student Run

```powershell
# Stanford student
D:/bybass/.venv/Scripts/python.exe run_production.py stanford_student "John Doe" "20240001"

# HUST student
D:/bybass/.venv/Scripts/python.exe run_production.py hust_student "Nguyen Van A" "20210001"
```

#### With SheerID URL (Full Automation)

```powershell
D:/bybass/.venv/Scripts/python.exe run_production.py stanford_student "John Doe" "20240001" --url "https://verify.sheerid.com/your-link"
```

#### Visible Browser (for Debugging)

```powershell
D:/bybass/.venv/Scripts/python.exe run_production.py stanford_student "John Doe" "20240001" --no-headless
```

#### Batch Processing from CSV

```powershell
# Process multiple students at once
D:/bybass/.venv/Scripts/python.exe run_production.py stanford_student --batch examples/students_stanford.csv

D:/bybass/.venv/Scripts/python.exe run_production.py hust_student --batch examples/students_hust.csv
```

---

### Method 2: Direct main.py Usage

For advanced customization, use `main.py` directly.

#### Basic Document Generation

```powershell
D:/bybass/.venv/Scripts/python.exe main.py `
    --university "Stanford University" `
    --name "John Doe" `
    --id "20240001"
```

#### Full Workflow with Browser Automation

```powershell
D:/bybass/.venv/Scripts/python.exe main.py `
    --university "Stanford University" `
    --name "John Michael Doe" `
    --id "20240001" `
    --url "https://verify.sheerid.com/..." `
    --headless
```

#### Custom Device and Processing

```powershell
D:/bybass/.venv/Scripts/python.exe main.py `
    --university "Hanoi University of Science and Technology" `
    --name "Nguyen Van A" `
    --id "20210001" `
    --template "bachkhoa_hanoi/enrollment.html" `
    --device "samsung_s23" `
    --intensity "heavy"
```

---

## 📋 Available Scenarios

### `stanford_student`
- **University**: Stanford University
- **Template**: Tuition bill
- **Device**: iPhone 13 Pro
- **Intensity**: Medium

### `hust_student`
- **University**: HUST
- **Template**: Enrollment verification
- **Device**: Samsung S23
- **Intensity**: Medium

---

## 📁 Production File Structure

```
d:\bybass/
├── config.py                      # Production configuration
├── run_production.py              # Production runner script
├── main.py                        # Core workflow engine
├── examples/                      # Example data
│   ├── students_stanford.csv     # Stanford batch example
│   └── students_hust.csv         # HUST batch example
├── output/                        # Generated documents
└── logs/                          # Production logs (auto-created)
```

---

## 🔧 Configuration

### Edit `config.py` for Your Environment

```python
# Proxy settings (if using residential proxies)
PROXY_CONFIG = {
    'server': 'http://your-proxy:port',
    'username': 'user',
    'password': 'pass'
}

# Browser settings
BROWSER_CONFIG = {
    'headless': True,
    'timeout': 120000,
}

# Default image processing
IMAGE_CONFIG = {
    'default_intensity': 'medium',
    'default_device': 'iphone_13_pro',
}
```

---

## 📊 CSV Format for Batch Processing

Create a CSV file with these columns:

```csv
name,id
John Doe,20240001
Jane Smith,20240002
```

**Fields:**
- `name`: Student full name
- `id`: Student ID number

---

## 🎯 Production Workflow Steps

### What Happens During Execution:

1. **Data Generation** (~1s)
   - Creates realistic student data
   - Renders HTML template with data

2. **Document Rendering** (~2s)
   - Converts HTML to PNG image
   - High-quality screenshot capture

3. **Image Processing** (~1-2s)
   - Applies perspective transform
   - Adds realistic noise and blur
   - Adjusts brightness/contrast
   - Adds shadow effects
   - JPEG compression

4. **Metadata Spoofing** (<1s, if ExifTool installed)
   - Strips existing metadata
   - Applies device-specific EXIF data
   - Sets realistic capture timestamp

5. **Browser Automation** (30-120s, if URL provided)
   - Opens SheerID verification page
   - Fills form with student data
   - Intercepts SSO requests
   - Uploads generated document
   - Waits for approval
   - Extracts discount code

**Total Time**: 3-5 seconds (document only) or 40-130 seconds (full automation)

---

## 📈 Output Files

Generated files are saved in `output/` directory:

```
output/
├── {university}_document_{timestamp}.png              # Raw rendered document
├── {university}_document_{timestamp}_realistic.jpg    # Processed realistic photo
```

**Example:**
```
output/stanford_document_20260105_182427.png
output/stanford_document_20260105_182427_realistic.jpg
```

---

## 🛡️ Production Best Practices

### 1. **Use Headless Mode**
```powershell
# Always use --headless in production for better performance
--headless
```

### 2. **Proxy Configuration**
```python
# Edit config.py to add residential proxies
PROXY_CONFIG = {
    'server': 'http://proxy:port',
    'username': 'user',
    'password': 'pass'
}
```

### 3. **Rate Limiting**
- Add delays between batch operations
- Use different proxies for each request
- Rotate device profiles

### 4. **Error Handling**
- Check exit codes (0 = success, 1 = failure)
- Review logs for detailed errors
- Implement retry logic for network issues

### 5. **Security**
- Never commit credentials to Git
- Use environment variables for sensitive data
- Keep `config.local.py` in `.gitignore`

---

## 🔍 Monitoring and Logging

### Check Logs

Logs are written to console and optionally to file:

```powershell
# View recent logs
Get-Content logs/production.log -Tail 50
```

### Exit Codes

- `0`: Success
- `1`: Error occurred

**Example:**
```powershell
D:/bybass/.venv/Scripts/python.exe main.py --university "Stanford" --name "John" --id "001"
echo $LASTEXITCODE  # Check exit code
```

---

## 🚨 Troubleshooting

### Issue: ExifTool Warnings

**Problem:** `WARNING: ExifTool not found`

**Solution:**
1. Download from https://exiftool.org/
2. Extract and rename to `exiftool.exe`
3. Add to PATH or place in project directory

### Issue: Browser Timeout

**Problem:** Browser automation times out

**Solution:**
- Increase timeout in `config.py`
- Use `--no-headless` to debug
- Check network connectivity

### Issue: Template Not Found

**Problem:** `Template not found: xyz.html`

**Solution:**
- Verify template exists in `templates/` directory
- Check template path matches folder structure
- Use `--template` flag with correct path

---

## 📞 Advanced Usage

### Custom Scenarios

Add new scenarios to `run_production.py`:

```python
SCENARIOS = {
    "my_custom_scenario": {
        "university": "My University",
        "template": "my_university/document.html",
        "device": "pixel_8_pro",
        "intensity": "light"
    }
}
```

### Integration with Other Systems

**API-like usage:**
```python
from main import SheerIDResearchApp
import asyncio

async def process_student(name, id):
    app = SheerIDResearchApp(config={
        'headless': True,
        'device_profile': 'iphone_13_pro'
    })
    
    results = await app.run_full_workflow(
        university="Stanford University",
        student_name=name,
        student_id=id,
        sheerid_url="skip"
    )
    
    return results['files']['final_document']

# Run
document_path = asyncio.run(process_student("John Doe", "20240001"))
```

---

## ✅ Production Checklist

Before running in production:

- [ ] ExifTool installed and in PATH
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Virtual environment activated
- [ ] Configuration reviewed in `config.py`
- [ ] Test run completed successfully
- [ ] Proxy settings configured (if needed)
- [ ] Logs directory exists
- [ ] Output directory has write permissions
- [ ] `.gitignore` includes sensitive files

---

## 📚 Related Documentation

- **README.md** - General overview and installation
- **HUONG_DAN.md** - Vietnamese guide and test results
- **Spec.ini** - Original technical specification

---

**Production Ready!** 🎉

For questions or issues, review the main README.md or check the logs directory.
