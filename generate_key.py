"""
Encryption Key Generator
Generates a secure Fernet encryption key for encrypting environment variables
"""
from cryptography.fernet import Fernet
import sys

def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

def main():
    print("=" * 70)
    print("[*] ENCRYPTION KEY GENERATOR")
    print("=" * 70)
    print()
    
    # Generate key
    encryption_key = generate_encryption_key()
    
    print("[OK] Generated Encryption Key:")
    print()
    print(f"   {encryption_key}")
    print()
    print("=" * 70)
    print("[!] IMPORTANT INSTRUCTIONS:")
    print("=" * 70)
    print()
    print("1. Copy the key above")
    print("2. Add to your .env file as:")
    print(f"   ENCRYPTION_KEY={encryption_key}")
    print()
    print("3. Keep this key SECRET and SECURE!")
    print("   - Do NOT commit to Git")
    print("   - Do NOT share publicly")
    print("   - Store in Azure Key Vault for production")
    print()
    print("4. If you lose this key, encrypted values CANNOT be decrypted!")
    print()
    print("=" * 70)
    print()
    
    # Ask if user wants to save to file
    try:
        save = input("Save key to encryption_key.txt? (y/n): ").strip().lower()
        if save == 'y':
            with open('encryption_key.txt', 'w') as f:
                f.write(encryption_key)
            print("[OK] Key saved to encryption_key.txt")
            print("[!] Remember to delete this file after copying to .env!")
    except KeyboardInterrupt:
        print("\n\n[X] Cancelled")
        sys.exit(0)

if __name__ == "__main__":
    main()
