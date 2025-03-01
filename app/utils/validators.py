import re
from datetime import datetime, time
import phonenumbers
from email_validator import EmailNotValidError
import bleach

def validate_email(email):
    """Check if the email address is valid"""
    try:
        validate_email_address(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Check if the password meets security criteria
    Requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least 8 characters long
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def validate_phone(phone):
    """Check if the phone number is valid"""
    try:
        parsed = phonenumbers.parse(phone, "TR")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def validate_identity_number(identity_number):
    """Check if the identity number is valid"""
    if not identity_number.isdigit() or len(identity_number) != 11:
        return False
    
    # Algorithm for first 10 digits
    digits = [int(d) for d in identity_number]
    if digits[0] == 0:
        return False
    
    # Final check
    if ((sum(digits[:10]) * 7) - sum(digits[1:9:2])) % 10 != digits[9]:
        return False
    if sum(digits[:10]) % 10 != digits[10]:
        return False
    
    return True

def validate_appointment_time(time):
    """Check if the appointment time is valid"""
    try:
        parsed_time = datetime.strptime(time, '%H:%M').time()
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('17:00', '%H:%M').time()
        return start_time <= parsed_time <= end_time
    except:
        return False

def validate_file_extension(filename, allowed_extensions):
    """Check if the file extension is in the allowed extensions list"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file_size, max_size):
    """Check if the file size is less than the maximum allowed size"""
    return file_size <= max_size

def sanitize_html(html_content):
    """Clean and secure HTML content"""
    return bleach.clean(
        html_content,
        tags=bleach.ALLOWED_TAGS + ['p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        attributes=bleach.ALLOWED_ATTRIBUTES
    )

def validate_date_range(start_date, end_date):
    """Check if the date range is valid"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return start <= end
    except:
        return False 