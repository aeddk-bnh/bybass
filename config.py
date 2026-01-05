# Production Configuration
# Copy this to config.local.py and customize for your environment

# Proxy Configuration (Optional - for residential proxies)
PROXY_CONFIG = {
    'server': 'http://proxy-server:port',
    'username': 'your-username',
    'password': 'your-password'
}

# SheerID Configuration
SHEERID_URLS = {
    'student_discount': 'https://verify.sheerid.com/student-discount',
    'teacher_discount': 'https://verify.sheerid.com/teacher-discount',
    # Add more verification URLs as needed
}

# Browser Settings
BROWSER_CONFIG = {
    'headless': True,  # Set to False for debugging
    'timeout': 120000,  # 2 minutes
    'slow_mo': 100,  # Slow down operations by 100ms
}

# Image Processing Settings
IMAGE_CONFIG = {
    'default_intensity': 'medium',  # 'light', 'medium', or 'heavy'
    'default_device': 'iphone_13_pro',  # Device profile for metadata
}

# University Templates Mapping
UNIVERSITY_TEMPLATES = {
    'stanford': {
        'name': 'Stanford University',
        'template': 'stanford/bill.html',
        'email_domain': 'stanford.edu',
        'type': 'tuition_bill'
    },
    'hust': {
        'name': 'Hanoi University of Science and Technology',
        'template': 'bachkhoa_hanoi/enrollment.html',
        'email_domain': 'hust.edu.vn',
        'type': 'enrollment'
    },
    # Add more universities here
}

# Form Field Selectors (Update based on actual SheerID form)
FORM_SELECTORS = {
    'first_name': '#firstName',
    'last_name': '#lastName',
    'email': '#email',
    'student_id': '#studentId',
    'file_upload': 'input[type="file"]',
    'submit_button': 'button[type="submit"]',
    'approval_message': '.approval-message, .success-message',
    'discount_code': '.discount-code, .promo-code'
}

# Logging Configuration
LOG_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'file': 'logs/production.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
