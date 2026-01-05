# Intelligent Retry System - Auto Bypass

## 🎯 Overview

Hệ thống retry thông minh tự động thử nhiều chiến lược khác nhau để bypass SheerID cho đến khi thành công.

## 🚀 Cách Hoạt Động

### 1. Các Chiến Lược (Strategies)

System sử dụng 4 chiến lược chính theo thứ tự ưu tiên:

#### Strategy 1: Email Domain Strategy (Nhanh nhất) 
- Tạo email với domain của trường (vd: john.doe@stanford.edu)
- SheerID thường tự động verify nếu email domain hợp lệ
- **Tỷ lệ thành công**: Cao với các trường lớn

#### Strategy 2: Form Fill Strategy (Cơ bản)
- Tự động điền tất cả các trường trong form
- Sử dụng data đã generate (tên, ID, email, ngày sinh)
- Submit và kiểm tra kết quả
- **Tỷ lệ thành công**: Trung bình

#### Strategy 3: Document Upload Strategy (Chi tiết)
- Upload document đã generate và xử lý realistic
- Kết hợp với điền form cơ bản
- Chờ approval tự động hoặc manual
- **Tỷ lệ thành công**: Cao nhưng mất thời gian hơn

#### Strategy 4: SSO Strategy (Dự phòng)
- Thử SSO login nếu có option
- Cần credentials thật nên thường skip
- **Tỷ lệ thành công**: Thấp (cần credentials)

### 2. Retry Logic

```
Cho mỗi round (tối đa 3 rounds):
    Cho mỗi strategy:
        - Thử execute strategy
        - Nếu SUCCESS → return ngay code
        - Nếu FAIL → chuyển sang strategy tiếp theo
        - Delay random 1.5-3s giữa mỗi strategy
    
    Delay 3-5s giữa mỗi round
    
Nếu tất cả fail → return kết quả cuối cùng
```

### 3. Configuration

Có thể tùy chỉnh trong `core/strategies.py`:

```python
class StrategyManager:
    def __init__(self):
        self.max_attempts_per_strategy = 3  # Số round thử
        self.max_total_attempts = 10        # Tổng số lần thử tối đa
```

## 📖 Sử dụng

### Cách 1: Tự động hoàn toàn

```bash
python auto_bypass.py "https://verify.sheerid.com/..."
```

System sẽ:
1. Analyze form
2. Generate data & document
3. Thử tất cả strategies cho đến khi thành công
4. Return discount code

### Cách 2: Với hints

```bash
# Hint về trường
python auto_bypass.py "https://verify.sheerid.com/..." --hint "Stanford"

# Xem browser (debug)
python auto_bypass.py "https://verify.sheerid.com/..." --show-browser
```

## 📊 Output Example

```
====================================================================
🚀 AUTO BYPASS SYSTEM STARTED
====================================================================

[STEP 1/5] 🔍 Analyzing SheerID form...
✓ Verification type: student
✓ Has SSO: False
✓ Has Upload: True

[STEP 2/5] 📝 Generating student data...
✓ University: Stanford University
✓ Student: John Smith (20240123)
✓ Email: john.smith@stanford.edu

[STEP 3/5] 🎨 Creating document...
✓ Rendered: output/stanford_document_xxx.png

[STEP 4/5] 🖼️  Processing image...
✓ Processed: output/stanford_document_xxx_realistic.jpg
✓ Device: iphone_14

[STEP 5/5] 🌐 Submitting with intelligent retry system...
🎯 System will try multiple strategies until success

====================================================================
🎯 STARTING INTELLIGENT RETRY SYSTEM
📋 4 strategies available
====================================================================

🔄 ROUND 1/3
----------------------------------------------------------------------

[Attempt 1] Strategy: Email Domain
Description: Generate and use university email address
✅ SUCCESS with Email Domain!
🎉 Code: ABC123XYZ

====================================================================
✅ BYPASS SUCCESSFUL!
🎉 Discount Code: ABC123XYZ
📊 Strategy: Email Domain
🔢 Total Attempts: 1
====================================================================
```

## 🔧 Thêm Custom Strategy

Tạo strategy mới trong `core/strategies.py`:

```python
class CustomStrategy(BypassStrategy):
    def __init__(self):
        super().__init__(
            name="My Custom Strategy",
            description="Description of what it does"
        )
    
    async def execute(self, context: Dict) -> StrategyResult:
        try:
            # Your logic here
            browser = context['browser']
            student_data = context['student_data']
            
            # Do something
            
            # Return success
            return StrategyResult(True, self.name, code="MYCODE")
        except Exception as e:
            return StrategyResult(False, self.name, error=str(e))
```

Đăng ký strategy:

```python
# Trong StrategyManager._register_strategies()
self.strategies = [
    EmailDomainStrategy(),
    CustomStrategy(),        # Thêm ở đây
    FormFillStrategy(),
    DocumentUploadStrategy(),
    SSOStrategy(),
]
```

## ⚙️ Advanced Settings

### Tùy chỉnh delays

Sửa trong strategy execute methods:

```python
# Delay giữa các actions
await asyncio.sleep(random.uniform(0.5, 1.5))

# Delay giữa strategies (trong StrategyManager)
await asyncio.sleep(random.uniform(3, 5))
```

### Tùy chỉnh detection

Sửa success indicators trong strategies:

```python
success_indicators = [
    'success', 'verified', 'approved', 
    'congratulations', 'discount', 'code'
]
```

### Tùy chỉnh code extraction patterns

```python
patterns = [
    r'code[:\s]+([A-Z0-9]{6,})',
    r'discount[:\s]+([A-Z0-9]{6,})',
    r'\b([A-Z0-9]{8,12})\b'
]
```

## 🎯 Best Practices

1. **Luôn test với --show-browser trước** để xem strategy nào work
2. **Tùy chỉnh delays** nếu bị rate limit
3. **Thêm success indicators** specific cho target site
4. **Log output** để phân tích strategy nào hiệu quả nhất
5. **Combine strategies** cho tỷ lệ thành công cao nhất

## ⚠️ Limitations

- SSO strategy cần real credentials
- Một số site có captcha/bot detection mạnh
- Rate limiting có thể block sau nhiều attempts
- Cần install ExifTool cho metadata spoofing hoàn chỉnh

## 🔍 Troubleshooting

### Tất cả strategies đều fail

1. Check logs để xem lỗi cụ thể
2. Chạy với `--show-browser` để debug
3. Kiểm tra selectors trong analyzer output
4. Thử adjust delays
5. Xem screenshots trong `output/` folder

### Strategy success nhưng không có code

- Code có thể được gửi qua email
- Check screenshot `verification_success.png`
- Có thể cần manual extraction

### Form không submit được

- Check selectors trong `core/analyzer.py`
- Site có thể có custom form structure
- Thử add custom selectors cho site đó
