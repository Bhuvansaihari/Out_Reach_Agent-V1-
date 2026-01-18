# 🔐 Environment Variable Encryption Guide

## Quick Start

### 1. Generate Encryption Key

```bash
python generate_key.py
```

Copy the generated key and add to your `.env`:
```env
ENCRYPTION_KEY=gAAAAABh...
```

### 2. Encrypt Sensitive Values

```bash
python encrypt_value.py
```

Follow the prompts to encrypt each sensitive value.

### 3. Update .env File

Replace plain values with encrypted ones:

**Before:**
```env
SENDGRID_API_KEY=SG.abc123xyz
```

**After:**
```env
SENDGRID_API_KEY=ENC:gAAAAABh1234567890...
```

### 4. Use in Code

```python
from config import get_config

# Auto-detects and decrypts ENC: values
api_key = get_config('SENDGRID_API_KEY')
```

---

## What to Encrypt

### ✅ Encrypt These (Sensitive):
- `SUPABASE_KEY`
- `SENDGRID_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `WEBHOOK_SECRET`
- Redis passwords (if any)

### ❌ Don't Encrypt These (Not Sensitive):
- `SUPABASE_URL`
- `SENDGRID_FROM_EMAIL`
- `TWILIO_PHONE_NUMBER`
- `CELERY_WORKER_CONCURRENCY`
- URLs without credentials

---

## Migration Steps

### Step 1: Generate Key
```bash
python generate_key.py
```

Output:
```
🔑 Generated Encryption Key:
gAAAAABh_abc123...

⚠️ IMPORTANT: Copy this to .env as ENCRYPTION_KEY
```

### Step 2: Add Key to .env
```env
ENCRYPTION_KEY=gAAAAABh_abc123...
```

### Step 3: Encrypt Each Value
```bash
python encrypt_value.py
```

Interactive session:
```
🔐 ENVIRONMENT VARIABLE ENCRYPTOR

✅ Encryption key loaded from .env

Enter the value to encrypt (input will be hidden):
Value: ********

✅ Encrypted successfully!

ENCRYPTED VALUE (copy this to your .env file):
   ENC:gAAAAABh1234567890abcdef...

Encrypt another value? (y/n): y
```

### Step 4: Update .env
Replace each plain value with its encrypted version:

```env
# Before
SENDGRID_API_KEY=SG.real_api_key_here

# After
SENDGRID_API_KEY=ENC:gAAAAABh1234567890abcdef...
```

### Step 5: Test Configuration
```bash
python config.py
```

Output shows which values are encrypted (🔐) vs plain (📝):
```
🧪 CONFIGURATION TEST

🔐 SENDGRID_API_KEY: SG.real_ap...
📝 SENDGRID_FROM_EMAIL: noreply@example.com
🔐 TWILIO_AUTH_TOKEN: abc123xyz...
```

---

## Code Integration

### Before (Plain os.getenv):
```python
import os
from dotenv import load_dotenv

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
```

### After (Auto-decrypting config):
```python
from config import get_config

SENDGRID_API_KEY = get_config("SENDGRID_API_KEY")
# Automatically decrypts if value starts with ENC:
```

### Convenience Functions:
```python
from config import (
    get_sendgrid_api_key,
    get_twilio_auth_token,
    get_supabase_key
)

# These auto-decrypt encrypted values
api_key = get_sendgrid_api_key()
token = get_twilio_auth_token()
key = get_supabase_key()
```

---

## Production Deployment (Azure)

### Option 1: Encrypted .env (Recommended)
1. Encrypt all sensitive values locally
2. Deploy `.env` with encrypted values
3. Store `ENCRYPTION_KEY` in Azure Key Vault
4. Load `ENCRYPTION_KEY` from Key Vault at runtime

### Option 2: Azure Key Vault Only
1. Don't use `.env` in production
2. Store all secrets in Azure Key Vault
3. Load directly from Key Vault (no encryption needed)

### Azure Key Vault Integration:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Get encryption key from Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
encryption_key = client.get_secret("ENCRYPTION-KEY").value

# Set as environment variable
os.environ['ENCRYPTION_KEY'] = encryption_key

# Now config.py can decrypt values
from config import get_config
api_key = get_config('SENDGRID_API_KEY')
```

---

## Security Best Practices

### ✅ DO:
- Generate a new encryption key for each environment (dev/staging/prod)
- Store `ENCRYPTION_KEY` in Azure Key Vault for production
- Add `encryption_key.txt` to `.gitignore`
- Rotate encryption keys periodically
- Use different keys for different projects

### ❌ DON'T:
- Commit `ENCRYPTION_KEY` to Git
- Share encryption keys via email/chat
- Reuse the same key across environments
- Store encryption key in plain text files
- Use weak or predictable keys

---

## Troubleshooting

### Error: "ENCRYPTION_KEY not found"
**Solution:** Run `generate_key.py` and add key to `.env`

### Error: "Decryption failed"
**Causes:**
- Wrong encryption key
- Corrupted encrypted value
- Value not properly encrypted

**Solution:** Re-encrypt the value with `encrypt_value.py`

### Warning: "Failed to decrypt, returning encrypted value"
**Cause:** Encryption key doesn't match the key used to encrypt

**Solution:** Verify `ENCRYPTION_KEY` in `.env` matches the key used during encryption

---

## Testing

### Test Encryption/Decryption:
```bash
# Test config loading
python config.py

# Expected output:
🔐 SENDGRID_API_KEY: SG.real_ap...  # Encrypted, auto-decrypted
📝 SENDGRID_FROM_EMAIL: noreply@... # Plain text
```

### Test in Python:
```python
from config import get_config

# Should return decrypted value
api_key = get_config('SENDGRID_API_KEY')
print(f"API Key: {api_key[:10]}...")  # SG.real_ap...
```

---

## Files Created

| File | Purpose |
|------|---------|
| `generate_key.py` | Generate encryption key |
| `encrypt_value.py` | Encrypt sensitive values |
| `config.py` | Configuration module with auto-decryption |
| `ENCRYPTION_GUIDE.md` | This guide |

---

## Example Workflow

```bash
# 1. Generate key
python generate_key.py
# Output: gAAAAABh... → Add to .env

# 2. Encrypt SendGrid API key
python encrypt_value.py
# Input: SG.abc123xyz
# Output: ENC:gAAAAABh1234... → Update .env

# 3. Encrypt Twilio token
python encrypt_value.py
# Input: abc123token
# Output: ENC:gAAAAABh5678... → Update .env

# 4. Test
python config.py
# Shows encrypted (🔐) and plain (📝) values

# 5. Run application
python -m uvicorn webhook_receiver.main:app --reload
# All encrypted values auto-decrypt at runtime!
```

---

## Support

If you encounter issues:
1. Check this guide
2. Run `python config.py` to test configuration
3. Verify `ENCRYPTION_KEY` is set correctly
4. Re-encrypt values if needed

---

**Remember:** Keep your `ENCRYPTION_KEY` secure! 🔒
