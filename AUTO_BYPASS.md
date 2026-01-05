# 🚀 Auto Bypass - Chỉ Cần Link!

## Cách Sử Dụng Đơn Giản Nhất

### 1. Chỉ cần nhập link SheerID:

```powershell
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..."
```

Hệ thống sẽ **TỰ ĐỘNG**:
- ✅ Phân tích form SheerID
- ✅ Nhận diện loại verification (student/teacher/military)
- ✅ Chọn template phù hợp
- ✅ Tạo thông tin sinh viên giả
- ✅ Render document chân thực
- ✅ Xử lý ảnh realistic
- ✅ Bypass SSO (nếu có)
- ✅ Upload document
- ✅ Lấy discount code

### 2. Với gợi ý trường (optional):

```powershell
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..." --hint "Stanford"
```

### 3. Hiển thị browser (để debug):

```powershell
D:/bybass/.venv/Scripts/python.exe auto_bypass.py "https://verify.sheerid.com/..." --show-browser
```

---

## 🎯 Auto Bypass Làm Gì?

### **Bước 1: Phân Tích Form (5s)**
```
🔍 Analyzing SheerID form...
✓ Verification type: student
✓ Has SSO: True
✓ Has Upload: True
```

Hệ thống tự động:
- Detect loại verification
- Tìm tất cả field bắt buộc
- Extract CSS selectors
- Kiểm tra SSO option
- Kiểm tra upload option

### **Bước 2: Tạo Dữ Liệu (1s)**
```
📝 Generating student data...
✓ University: Stanford University
✓ Student: Michael Brown (20230234)
✓ Email: michael.brown@stanford.edu
```

Hệ thống tự động tạo:
- Tên sinh viên realistic
- Student ID format đúng
- Email với domain phù hợp
- Ngày sinh hợp lệ

### **Bước 3: Tạo Document (2s)**
```
🎨 Creating document...
✓ Rendered: output/stanford_document_20260105_183045.png
```

### **Bước 4: Xử Lý Ảnh (1s)**
```
🖼️  Processing image...
✓ Processed: output/stanford_document_20260105_183045_realistic.jpg
✓ Device: iphone_13_pro
```

Tự động apply:
- Perspective transform
- Gaussian noise
- Blur effects
- JPEG compression
- EXIF metadata spoofing

### **Bước 5: Submit & Extract (30-120s)**
```
🌐 Submitting to SheerID...
✓ Filling form fields...
✓ Selected organization: Stanford University
✓ Enabling SSO bypass...
✓ Uploading document...
✓ Submitting form...
⏳ Waiting for verification...

✅ BYPASS SUCCESSFUL!
🎉 Discount Code: STUDENT2024ABC
```

---

## 📊 Kết Quả Tự Động

```
============================================================
📊 FINAL RESULTS
============================================================
Success: ✅ YES

Generated Identity:
  Name: Michael Brown
  ID: 20230234
  Email: michael.brown@stanford.edu
  University: Stanford University

Generated Files:
  raw_image: output/stanford_document_20260105_183045.png
  processed_image: output/stanford_document_20260105_183045_realistic.jpg
  final_document: output/stanford_document_20260105_183045_realistic.jpg

🎉 Discount Code: STUDENT2024ABC
============================================================
```

---

## 🧠 Auto Bypass Intelligence

### Form Analysis Engine
```python
# Tự động detect:
- Verification type (student/teacher/military)
- Required fields
- Form selectors
- SSO availability
- Upload option
- Organization/university
```

### Smart Template Selection
```python
# Auto chọn template dựa trên:
- Verification type detected
- University hint (nếu có)
- Random selection từ template pool
```

### Realistic Data Generation
```python
# Tự động tạo:
- First/Last names realistic
- Student ID format đúng
- Email với domain phù hợp
- Birth date hợp lệ
```

### Intelligent Form Filling
```python
# Auto điền form:
- Tìm và điền tất cả fields
- Auto-select organization từ dropdown
- Handle SSO bypass
- Upload document
- Click submit
```

---

## 🎬 So Sánh: Trước vs Sau

### ❌ Trước (Phức Tạp):

```powershell
# Phải tự nhập tất cả thông tin
python main.py `
    --university "Stanford University" `
    --name "John Michael Doe" `
    --id "20240001" `
    --url "https://verify.sheerid.com/..." `
    --template "stanford/bill.html" `
    --device "iphone_13_pro" `
    --intensity "medium" `
    --headless
```

### ✅ Sau (Siêu Đơn Giản):

```powershell
# CHỈ CẦN LINK!
python auto_bypass.py "https://verify.sheerid.com/..."
```

---

## 🔧 Advanced Options

### Chỉ định trường cụ thể:
```powershell
python auto_bypass.py "https://verify.sheerid.com/..." --hint "Harvard"
```

### Debug mode (xem browser):
```powershell
python auto_bypass.py "https://verify.sheerid.com/..." --show-browser
```

---

## 📝 Supported Templates

Hiện tại hỗ trợ tự động:

### Student Verification
- ✅ Stanford University (US)
- ✅ Hanoi University of Science and Technology (Vietnam)

**Dễ dàng thêm template mới** bằng cách edit `auto_bypass.py`:

```python
TEMPLATES = {
    'student': [
        ('stanford', 'Stanford University', 'stanford/bill.html', 'stanford.edu'),
        ('hust', 'HUST', 'bachkhoa_hanoi/enrollment.html', 'hust.edu.vn'),
        # Thêm template mới ở đây
        ('harvard', 'Harvard University', 'harvard/bill.html', 'harvard.edu'),
    ]
}
```

---

## ⚡ Performance

| Step | Time |
|------|------|
| Form Analysis | ~5s |
| Data Generation | ~1s |
| Document Creation | ~2s |
| Image Processing | ~1s |
| Form Submission | ~30-120s |
| **TOTAL** | **~40-130s** |

---

## 🛡️ What Gets Bypassed

✅ **SSO Authentication** - Tự động chặn SSO requests  
✅ **Document Verification** - Upload document giả realistic  
✅ **Form Validation** - Điền đúng format tất cả fields  
✅ **Bot Detection** - Stealth browser với fingerprint spoofing  
✅ **Metadata Checks** - EXIF data giống ảnh chụp thật  

---

## 🚨 Error Handling

Nếu bypass fail, hệ thống sẽ:
1. ✅ Save screenshot để debug
2. ✅ Log chi tiết lỗi
3. ✅ Suggest manual steps
4. ✅ Giữ lại generated files

---

## 💡 Tips

1. **Lần đầu run**: Dùng `--show-browser` để xem flow
2. **Multi-account**: Chạy nhiều lần, mỗi lần tạo identity mới
3. **Custom template**: Thêm template của trường bạn vào `TEMPLATES`
4. **Debug**: Check `output/verification_*.png` nếu fail

---

## ✨ Magic Commands

```powershell
# Cách dễ nhất - Just paste link!
python auto_bypass.py "PASTE_LINK_HERE"

# Với hint trường
python auto_bypass.py "LINK" --hint "Stanford"

# Debug mode
python auto_bypass.py "LINK" --show-browser
```

---

**Tất cả trong một lệnh duy nhất! 🎉**
