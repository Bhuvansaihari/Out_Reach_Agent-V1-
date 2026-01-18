"""
Configuration Module with Encryption Support
Centralized configuration management with automatic decryption of encrypted values
"""
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from typing import Optional, Any
from functools import lru_cache

# Load environment variables
load_dotenv()

# Cache for decrypted values (performance optimization)
_decryption_cache = {}

def _get_fernet() -> Optional[Fernet]:
    """
    Get Fernet cipher instance
    
    Returns:
        Fernet instance or None if no encryption key
    """
    encryption_key = os.getenv('ENCRYPTION_KEY')
    if not encryption_key:
        return None
    
    try:
        return Fernet(encryption_key.encode())
    except Exception as e:
        print(f"⚠️ Warning: Invalid ENCRYPTION_KEY: {e}")
        return None

def _decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt an encrypted value
    
    Args:
        encrypted_value: Encrypted value (with or without ENC: prefix)
    
    Returns:
        Decrypted plain text value
    
    Raises:
        ValueError: If decryption fails
    """
    # Remove ENC: prefix if present
    if encrypted_value.startswith('ENC:'):
        encrypted_value = encrypted_value[4:]
    
    # Check cache first
    if encrypted_value in _decryption_cache:
        return _decryption_cache[encrypted_value]
    
    # Get Fernet cipher
    fernet = _get_fernet()
    if not fernet:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    
    try:
        # Decrypt
        decrypted = fernet.decrypt(encrypted_value.encode()).decode()
        
        # Cache the result
        _decryption_cache[encrypted_value] = decrypted
        
        return decrypted
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

def get_config(key: str, default: Any = None, encrypted: Optional[bool] = None) -> Any:
    """
    Get configuration value with optional automatic decryption
    
    Args:
        key: Environment variable name
        default: Default value if key not found
        encrypted: Force decryption (True), force plain (False), or auto-detect (None)
    
    Returns:
        Configuration value (decrypted if encrypted)
    
    Examples:
        # Auto-detect encryption (recommended)
        api_key = get_config('SENDGRID_API_KEY')
        
        # Force decryption
        api_key = get_config('SENDGRID_API_KEY', encrypted=True)
        
        # Force plain (no decryption)
        email = get_config('SENDGRID_FROM_EMAIL', encrypted=False)
        
        # With default value
        port = get_config('PORT', default=8000)
    """
    value = os.getenv(key, default)
    
    if value is None:
        return default
    
    # Convert to string for processing
    value_str = str(value)
    
    # Auto-detect encryption if not specified
    if encrypted is None:
        encrypted = value_str.startswith('ENC:')
    
    # Decrypt if needed
    if encrypted and value_str.startswith('ENC:'):
        try:
            return _decrypt_value(value_str)
        except ValueError as e:
            print(f"⚠️ Warning: Failed to decrypt {key}: {e}")
            print(f"   Returning encrypted value as-is")
            return value_str
    
    return value_str

def get_config_int(key: str, default: int = 0) -> int:
    """
    Get configuration value as integer
    
    Args:
        key: Environment variable name
        default: Default value if key not found or conversion fails
    
    Returns:
        Integer value
    """
    value = get_config(key)
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"⚠️ Warning: Cannot convert {key}={value} to int, using default {default}")
        return default

def get_config_bool(key: str, default: bool = False) -> bool:
    """
    Get configuration value as boolean
    
    Args:
        key: Environment variable name
        default: Default value if key not found
    
    Returns:
        Boolean value
    
    Note:
        Treats 'true', '1', 'yes', 'on' as True (case-insensitive)
    """
    value = get_config(key)
    if value is None:
        return default
    
    return str(value).lower() in ('true', '1', 'yes', 'on')

def get_config_list(key: str, separator: str = ',', default: list = None) -> list:
    """
    Get configuration value as list
    
    Args:
        key: Environment variable name
        separator: Separator character (default: comma)
        default: Default value if key not found
    
    Returns:
        List of strings
    
    Example:
        ALLOWED_HOSTS=localhost,example.com,api.example.com
        hosts = get_config_list('ALLOWED_HOSTS')
        # Returns: ['localhost', 'example.com', 'api.example.com']
    """
    value = get_config(key)
    if value is None:
        return default or []
    
    return [item.strip() for item in str(value).split(separator) if item.strip()]

# Convenience functions for common config values
def get_supabase_url() -> str:
    """Get Supabase URL"""
    return get_config('SUPABASE_URL', default='')

def get_supabase_key() -> str:
    """Get Supabase key (auto-decrypts if encrypted)"""
    return get_config('SUPABASE_KEY')

def get_sendgrid_api_key() -> str:
    """Get SendGrid API key (auto-decrypts if encrypted)"""
    return get_config('SENDGRID_API_KEY')

def get_sendgrid_from_email() -> str:
    """Get SendGrid from email"""
    return get_config('SENDGRID_FROM_EMAIL', default='')

def get_twilio_account_sid() -> str:
    """Get Twilio Account SID (auto-decrypts if encrypted)"""
    return get_config('TWILIO_ACCOUNT_SID')

def get_twilio_auth_token() -> str:
    """Get Twilio Auth Token (auto-decrypts if encrypted)"""
    return get_config('TWILIO_AUTH_TOKEN')

def get_twilio_phone_number() -> str:
    """Get Twilio phone number"""
    return get_config('TWILIO_PHONE_NUMBER', default='')

def get_webhook_secret() -> str:
    """Get webhook secret (auto-decrypts if encrypted)"""
    return get_config('WEBHOOK_SECRET')

def get_celery_broker_url() -> str:
    """Get Celery broker URL"""
    return get_config('CELERY_BROKER_URL', default='redis://localhost:6379/0')

def get_celery_result_backend() -> str:
    """Get Celery result backend URL"""
    return get_config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

def get_celery_worker_concurrency() -> int:
    """Get Celery worker concurrency"""
    return get_config_int('CELERY_WORKER_CONCURRENCY', default=20)

# Test function
def test_config():
    """Test configuration loading and decryption"""
    print("=" * 70)
    print("🧪 CONFIGURATION TEST")
    print("=" * 70)
    print()
    
    test_keys = [
        'ENCRYPTION_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SENDGRID_API_KEY',
        'SENDGRID_FROM_EMAIL',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER',
        'WEBHOOK_SECRET',
        'CELERY_BROKER_URL',
        'CELERY_WORKER_CONCURRENCY',
    ]
    
    for key in test_keys:
        value = get_config(key)
        if value:
            # Mask sensitive values
            if key in ['ENCRYPTION_KEY', 'SUPABASE_KEY', 'SENDGRID_API_KEY', 
                       'TWILIO_AUTH_TOKEN', 'WEBHOOK_SECRET']:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            
            encrypted_marker = '🔐' if os.getenv(key, '').startswith('ENC:') else '📝'
            print(f"{encrypted_marker} {key}: {display_value}")
        else:
            print(f"❌ {key}: NOT SET")
    
    print()
    print("=" * 70)
    print()
    print("Legend:")
    print("  🔐 = Encrypted value (auto-decrypted)")
    print("  📝 = Plain text value")
    print("  ❌ = Not set")
    print()

if __name__ == "__main__":
    test_config()
