from typing import Dict
import re
import json

def extract_plain_description(raw_desc):
    """
    Accepts a job description string that may be:
      - Plain text
      - JSON string with a 'description' key (as produced by some parsers/storage)
    Returns only the intended plain text.
    """
    try:
        jd_obj = json.loads(raw_desc)
        if isinstance(jd_obj, dict) and "description" in jd_obj:
            return jd_obj["description"]
    except Exception:
        pass
    return raw_desc

def format_single_requirement(requirement: Dict) -> str:
    description = extract_plain_description(requirement.get('requirement_description', 'N/A'))    
    if len(description) > 300:
        description = description[:300] + '...'
    similarity_score = requirement.get('similarity_score', 0.0)
    match_percentage = f"{similarity_score * 100:.1f}%" if similarity_score else "N/A"
    min_pay = requirement.get('min_payrate')
    max_pay = requirement.get('max_payrate')
    if min_pay and max_pay:
        if min_pay == max_pay:
            pay_rate_str = f"${float(min_pay):.2f}/hr"
        else:
            pay_rate_str = f"${float(min_pay):.2f} - ${float(max_pay):.2f}/hr"
    elif min_pay:
        pay_rate_str = f"${float(min_pay):.2f}+/hr"
    elif max_pay:
        pay_rate_str = f"Up to ${float(max_pay):.2f}/hr"
    else:
        pay_rate_str = "Negotiable"
    duration = requirement.get('requirement_duration')
    duration_str = str(duration).strip() if duration else "Not specified"
    open_date = requirement.get('requirement_open_date')
    open_date_str = str(open_date) if open_date else "ASAP"
    location = requirement.get('location', 'Remote')
    formatted = f"""
    Job Requirement:
    - Title: {requirement.get('requirement_title', 'N/A')}
    - Client: {requirement.get('client_name', 'N/A')}
    - Location: {location}
    - Pay Rate: {pay_rate_str}
    - Duration: {duration_str}
    - Start Date: {open_date_str}
    - Match Score: {match_percentage}
    - Description: {description}
    """
    return formatted.strip()

def extract_first_name(full_name: str) -> str:
    if not full_name:
        return "Candidate"
    parts = full_name.strip().split()
    return parts[0] if parts else "Candidate"

def format_phone_number(phone: str, default_country_code: str = "+1") -> str:
    if not phone:
        return None
    phone = re.sub(r'[^\d+]', '', phone)
    if phone.startswith('+'):
        return phone
    return f"{default_country_code}{phone}"

def validate_phone_number(phone: str) -> bool:
    if not phone:
        return False
    pattern = r'^\+\d{10,15}$'
    return bool(re.match(pattern, phone))

def validate_webhook_payload(payload: dict) -> bool:
    required_fields = ['type', 'table', 'record']
    for field in required_fields:
        if field not in payload:
            print(f"❌ Missing required field: {field}")
            return False
    record = payload.get('record', {})
    if 'cand_id' not in record:
        print("❌ Missing cand_id in record")
        return False
    if 'requirement_id' not in record:
        print("❌ Missing requirement_id in record")
        return False
    return True