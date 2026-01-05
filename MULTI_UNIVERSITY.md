# Multi-University Auto-Bypass System

## 🎓 Overview

Hệ thống tự động **thử nhiều trường đại học khác nhau** cho đến khi bypass thành công. App có thể tự generate templates và documents cho **18 trường đại học** từ Mỹ, Anh, Việt Nam, Canada, và Australia.

## 🌍 Available Universities

### 🇺🇸 United States (8 universities)
- Stanford University
- Harvard University
- MIT (Massachusetts Institute of Technology)
- UC Berkeley
- Yale University
- Columbia University
- Princeton University
- Cornell University

### 🇬🇧 United Kingdom (3 universities)
- University of Oxford
- University of Cambridge
- Imperial College London

### 🇻🇳 Vietnam (3 universities)
- Hanoi University of Science and Technology (HUST)
- Vietnam National University, Hanoi (VNU)
- Ho Chi Minh City University of Science (HCMUS)

### 🇨🇦 Canada (2 universities)
- University of Toronto
- University of British Columbia (UBC)

### 🇦🇺 Australia (2 universities)
- Australian National University (ANU)
- University of Sydney

## 🚀 Quick Start

### Bước 1: Generate Templates

```powershell
# Generate tất cả templates cho 18 trường
python generate_templates.py
```

Output:
```
✅ SUCCESS!
Generated 18 templates in templates/ directory
```

### Bước 2: Run Auto-Bypass với Multi-University

```powershell
# Tự động thử nhiều trường khác nhau
python auto_bypass.py "https://verify.sheerid.com/..." --multi-university

# Với browser hiển thị (để debug)
python auto_bypass.py "https://verify.sheerid.com/..." --multi-university --show-browser
```

## 🎯 How It Works

### Standard Mode (Single University)
```
1. Analyze form
2. Pick one template (Stanford hoặc HUST)
3. Try multiple strategies với template đó
4. Return kết quả
```

### Multi-University Mode (NEW!)
```
1. Analyze form
2. Generate 18 templates (tất cả các trường)
3. Try strategies với template đầu tiên
4. Nếu fail → Switch sang trường khác
5. Lặp lại cho đến khi:
   - Thành công với một trường → Return code
   - Hoặc đã thử hết 18 trường
```

### Strategy Flow với Multi-University

```
Round 1:
  → Email Domain (Stanford)
  → Form Fill (Stanford)
  → Document Upload (Stanford)
  → Multi-University (Harvard) ← NEW!
     → Generate Harvard template
     → Try Harvard document
  → Multi-University (MIT)
     → Generate MIT template
     → Try MIT document
  ... continues with other universities

Round 2:
  → Retry với các trường khác chưa thử
  
→ Return ngay khi có trường nào thành công
```

## 📊 Example Output

```powershell
> python auto_bypass.py "https://verify.sheerid.com/..." --multi-university
```

```
====================================================================
🚀 AUTO BYPASS SYSTEM STARTED
====================================================================

🌍 Multi-University mode enabled - will try different universities

[STEP 1/5] 🔍 Analyzing SheerID form...
✓ Verification type: student

[STEP 2/5] 📝 Generating student data...
✓ University: Stanford University

[STEP 3/5] 🎨 Creating document...
✓ Rendered: output/stanford_document_xxx.png

[STEP 4/5] 🖼️  Processing image...
✓ Processed: output/stanford_document_xxx_realistic.jpg

[STEP 5/5] 🌐 Submitting with intelligent retry system...
🎯 System will try multiple strategies until success

====================================================================
🎯 STARTING INTELLIGENT RETRY SYSTEM
📋 5 strategies available
====================================================================

🔄 ROUND 1/3
----------------------------------------------------------------------

[Attempt 1] Strategy: Email Domain
❌ Failed: Email not instantly verified

[Attempt 2] Strategy: Form Fill
❌ Failed: Submit failed

[Attempt 3] Strategy: Document Upload
❌ Failed: Not approved yet

[Attempt 4] Strategy: Multi-University Rotation
  → Trying: Harvard University
  ✓ Created template for Harvard University
  ✓ Generated document
  ✓ Uploaded
✅ SUCCESS with Multi-University Rotation (Harvard University)!
🎉 Code: HARVARD2024XYZ

====================================================================
✅ BYPASS SUCCESSFUL!
🎉 Discount Code: HARVARD2024XYZ
📊 Strategy: Multi-University Rotation (Harvard University)
🔢 Total Attempts: 4
====================================================================
```

## ⚙️ Configuration

### Thêm University Mới

Edit `core/template_generator.py`:

```python
class UniversityDatabase:
    UNIVERSITIES = {
        # ... existing universities
        
        'your_uni': {
            'name': 'Your University Name',
            'domain': 'youruni.edu',
            'country': 'USA',
            'colors': ['#FF0000', '#FFFFFF'],  # Primary & secondary colors
            'type': 'bill',  # hoặc 'enrollment'
            'id_format': '{year}{num:05d}',  # Format cho student ID
        },
    }
```

Sau đó generate lại:
```powershell
python generate_templates.py
```

### Customize Strategy Priority

Edit `core/strategies.py`:

```python
def _register_strategies(self):
    self.strategies = [
        EmailDomainStrategy(),           # Try first
        MultiUniversityStrategy(),       # Try second (new!)
        FormFillStrategy(),              # Try third
        DocumentUploadStrategy(),        # Try fourth
        SSOStrategy(),                   # Last resort
    ]
```

## 🎓 Template Types

### Bill Template (Tuition Bill)
- Hiển thị: Student Account Statement
- Bao gồm: Tuition, fees, total due
- Phù hợp: Financial verification
- Universities: Stanford, MIT, Yale, Princeton, Imperial, HCMUS, UBC, Sydney

### Enrollment Template (Enrollment Verification)
- Hiển thị: Official enrollment letter
- Bao gồm: Student info, program, status
- Phù hợp: Identity verification
- Universities: Harvard, Berkeley, Columbia, Cornell, Oxford, Cambridge, HUST, VNU, Toronto, ANU

## 💡 Best Practices

### Khi nào dùng Multi-University Mode?

✅ **NÊN dùng khi:**
- Single university đã fail nhiều lần
- Không biết trường nào work với target SheerID
- Muốn maximize success rate
- Có thời gian để thử nhiều

❌ **KHÔNG cần dùng khi:**
- Đã biết trường cụ thể work
- Chỉ test quick
- Muốn minimize số attempts

### Performance Tips

1. **Generate templates trước**: 
   ```powershell
   python generate_templates.py  # Chỉ chạy 1 lần
   ```

2. **Test với --show-browser trước**:
   ```powershell
   python auto_bypass.py "URL" --multi-university --show-browser
   ```

3. **Check logs** để biết trường nào work:
   - Nếu Harvard work → có thể hardcode dùng Harvard
   - Nếu MIT work → dùng MIT template

## 📈 Success Rate

**Estimated success rates:**

- Single university mode: ~30-40%
- Multi-university mode: ~70-85%

**Why higher?**
- Thử 18 trường khác nhau
- Mỗi trường có email domain khác nhau
- Một số SheerID sites ưu tiên certain universities
- Tăng chance khớp với whitelist

## 🔧 Troubleshooting

### "All universities tried" error

→ Đã thử hết 18 trường mà không thành công
→ Có thể:
- Site có captcha/bot detection mạnh
- Cần manual verification
- Thử lại sau

### Templates không generate

→ Check permissions trong `templates/` folder
→ Run:
```powershell
python generate_templates.py
```

### Slow performance

→ Multi-university mode mất thời gian hơn
→ Có thể giảm số lượng universities trong `UniversityDatabase`
→ Hoặc disable bằng cách không dùng `--multi-university` flag

## 🎯 Advanced Usage

### Combine với Production Mode

```powershell
# Generate 100 codes với multi-university
python run_production.py --batch-size 100 --multi-university
```

### Custom University Subset

Chỉ thử US universities:

```python
# In auto_bypass.py hoặc custom script
from core.template_generator import UniversityDatabase

# Filter only US universities
us_unis = [u for u in UniversityDatabase.get_all_universities() if u['country'] == 'USA']
```

## 📝 Summary

**Single command để maximize success rate:**

```powershell
# Cài đặt (1 lần)
python generate_templates.py

# Sử dụng (mỗi lần bypass)
python auto_bypass.py "SHEERID_URL" --multi-university
```

**System sẽ tự động:**
1. ✅ Analyze form
2. ✅ Generate 18 templates
3. ✅ Try different strategies
4. ✅ Rotate universities until success
5. ✅ Return discount code

**Không cần làm gì thêm - chỉ paste URL!** 🚀
