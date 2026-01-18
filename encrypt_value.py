"""
Environment Variable Encryptor
Interactive script to encrypt sensitive values for .env file
"""
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import sys
import getpass

def encrypt_value(value: str, encryption_key: str) -> str:
    """
    Encrypt a value using Fernet encryption
    
    Args:
        value: Plain text value to encrypt
        encryption_key: Base64 encoded Fernet key
    
    Returns:
        Encrypted value with ENC: prefix
    """
    fernet = Fernet(encryption_key.encode())
    encrypted = fernet.encrypt(value.encode())
    return f"ENC:{encrypted.decode()}"

def main():
    print("=" * 70)
    print("[*] ENVIRONMENT VARIABLE ENCRYPTOR")
    print("=" * 70)
    print()
    
    # Load .env to get encryption key
    load_dotenv()
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        print("[X] ERROR: ENCRYPTION_KEY not found in .env file")
        print()
        print("Please run generate_key.py first and add the key to .env:")
        print("   ENCRYPTION_KEY=<generated-key>")
        print()
        sys.exit(1)
    
    print("[OK] Encryption key loaded from .env")
    print()
    print("-" * 70)
    print()
    
    try:
        while True:
            # Get value to encrypt (hidden input)
            print("Enter the value to encrypt (input will be hidden):")
            value = getpass.getpass("Value: ")
            
            if not value:
                print("[X] Empty value, please try again")
                print()
                continue
            
            # Encrypt the value
            encrypted_value = encrypt_value(value, encryption_key)
            
            print()
            print("[OK] Encrypted successfully!")
            print()
            print("=" * 70)
            print("ENCRYPTED VALUE (copy this to your .env file):")
            print("=" * 70)
            print()
            print(f"   {encrypted_value}")
            print()
            print("=" * 70)
            print()
            
            # Ask if user wants to encrypt another value
            another = input("Encrypt another value? (y/n): ").strip().lower()
            if another != 'y':
                print()
                print("[OK] Done! Remember to update your .env file with encrypted values.")
                print()
                break
            
            print()
            print("-" * 70)
            print()
    
    except KeyboardInterrupt:
        print("\n\n[X] Cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
